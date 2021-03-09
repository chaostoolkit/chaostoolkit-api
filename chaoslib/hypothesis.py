# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation
from functools import singledispatch
import json
from numbers import Number
import re
from typing import Any, Dict

try:
    from jsonpath2.path import Path as JSONPath
    HAS_JSONPATH = True
except ImportError:
    HAS_JSONPATH = False

from logzero import logger

from chaoslib import substitute
from chaoslib.activity import ensure_activity_is_valid, execute_activity, \
    run_activity
from chaoslib.control import controls
from chaoslib.exceptions import ActivityFailed, InvalidActivity, \
    InvalidExperiment
from chaoslib.types import Configuration, Experiment, \
    Secrets, Tolerance


__all__ = ["ensure_hypothesis_is_valid", "run_steady_state_hypothesis"]


def ensure_hypothesis_is_valid(experiment: Experiment):
    """
    Validates that the steady state hypothesis entry has the expected schema
    or raises :exc:`InvalidExperiment` or :exc:`InvalidActivity`.
    """
    hypo = experiment.get("steady-state-hypothesis")
    if hypo is None:
        return

    if not hypo.get("title"):
        raise InvalidExperiment("hypothesis requires a title")

    probes = hypo.get("probes")
    if probes:
        for probe in probes:
            ensure_activity_is_valid(probe)

            if "tolerance" not in probe:
                raise InvalidActivity(
                    "hypothesis probe must have a tolerance entry")

            ensure_hypothesis_tolerance_is_valid(probe["tolerance"])


def ensure_hypothesis_tolerance_is_valid(tolerance: Tolerance):
    """
    Validate the tolerance of the hypothesis probe and raises
    :exc:`InvalidActivity` if it isn't valid.
    """
    if not isinstance(tolerance, (
            bool, int, list, str, dict)):
        raise InvalidActivity(
            "hypothesis probe tolerance must either be an integer, "
            "a string, a boolean or a pair of values for boundaries. "
            "It can also be a dictionary which is a probe activity "
            "definition that takes an argument called `value` with "
            "the value of the probe itself to be validated")

    if isinstance(tolerance, dict):
        tolerance_type = tolerance.get("type")

        if tolerance_type == "probe":
            ensure_activity_is_valid(tolerance)
        elif tolerance_type == "regex":
            check_regex_pattern(tolerance)
        elif tolerance_type == "jsonpath":
            check_json_path(tolerance)
        elif tolerance_type == "range":
            check_range(tolerance)
        else:
            raise InvalidActivity(
                "hypothesis probe tolerance type '{}' is unsupported".format(
                    tolerance_type))


def check_regex_pattern(tolerance: Tolerance):
    """
    Check the regex pattern of a tolerance and raise :exc:`InvalidActivity`
    when the pattern is missing or invalid (meaning, cannot be compiled by
    the Python regex engine).
    """
    if "pattern" not in tolerance:
        raise InvalidActivity(
            "hypothesis regex probe tolerance must have a `pattern` key")

    pattern = tolerance["pattern"]
    try:
        re.compile(pattern)
    except TypeError:
        raise InvalidActivity(
            "hypothesis probe tolerance pattern {} has an invalid type".format(
                pattern))
    except re.error as e:
        raise InvalidActivity(
            "hypothesis probe tolerance pattern {} seems invalid: {}".format(
                e.pattern, e.msg))


def check_json_path(tolerance: Tolerance):
    """
    Check the JSON path of a tolerance and raise :exc:`InvalidActivity`
    when the path is missing or invalid.

    See: https://github.com/h2non/jsonpath-ng
    """
    if not HAS_JSONPATH:
        raise InvalidActivity(
            "Install the `jsonpath2` package to use a JSON path tolerance: "
            "`pip install chaostoolkit-lib[jsonpath]`.")

    if "path" not in tolerance:
        raise InvalidActivity(
            "hypothesis jsonpath probe tolerance must have a `path` key")

    try:
        path = tolerance.get("path", "").strip()
        if not path:
            raise InvalidActivity(
                "hypothesis probe tolerance JSON path cannot be empty")
        JSONPath.parse_str(path)
    except ValueError:
        raise InvalidActivity(
            "hypothesis probe tolerance JSON path {} is invalid".format(
                path))
    except TypeError:
        raise InvalidActivity(
            "hypothesis probe tolerance JSON path {} has an invalid "
            "type".format(path))


def check_range(tolerance: Tolerance):
    """
    Check a value is within a given range. That range may be set to a min and
    max value or a sequence.
    """
    if "range" not in tolerance:
        raise InvalidActivity(
            "hypothesis range probe tolerance must have a `range` key")

    the_range = tolerance["range"]
    if not isinstance(the_range, list):
        raise InvalidActivity(
            "hypothesis range must be a sequence")

    if len(the_range) != 2:
        raise InvalidActivity(
            "hypothesis range sequence must be made of two values")

    if not isinstance(the_range[0], Number):
        raise InvalidActivity(
            "hypothesis range lower boundary must be a number")

    if not isinstance(the_range[1], Number):
        raise InvalidActivity(
            "hypothesis range upper boundary must be a number")


def run_steady_state_hypothesis(experiment: Experiment,
                                configuration: Configuration, secrets: Secrets,
                                dry: bool = False) -> Dict[str, Any]:
    """
    Run all probes in the hypothesis and fail the experiment as soon as any of
    the probe fails or is outside the tolerance zone.
    """
    state = {
        "steady_state_met": None,
        "probes": []
    }
    hypo = experiment.get("steady-state-hypothesis")
    if not hypo:
        logger.debug("No hypothesis declared.")
        return

    logger.info("Steady state hypothesis: {h}".format(h=hypo.get("title")))

    with controls(level="hypothesis", experiment=experiment, context=hypo,
                  configuration=configuration, secrets=secrets) as control:
        probes = hypo.get("probes", [])
        control.with_state(state)

        for activity in probes:
            run = execute_activity(
                experiment=experiment, activity=activity,
                configuration=configuration, secrets=secrets, dry=dry)

            state["probes"].append(run)

            if run["status"] == "failed":
                run["tolerance_met"] = False
                state["steady_state_met"] = False
                logger.warning("Probe terminated unexpectedly, "
                               "so its tolerance could not be validated")
                return state

            run["tolerance_met"] = True

            if dry:
                # do not check for tolerance when dry mode is on
                continue

            tolerance = activity.get("tolerance")
            logger.debug("allowed tolerance is {t}".format(t=str(tolerance)))
            checked = within_tolerance(
                tolerance, run["output"], configuration=configuration,
                secrets=secrets)
            if not checked:
                run["tolerance_met"] = False
                state["steady_state_met"] = False
                return state

        state["steady_state_met"] = True
        logger.info("Steady state hypothesis is met!")

    return state


@singledispatch
def within_tolerance(tolerance: Any, value: Any,
                     configuration: Configuration = None,
                     secrets: Secrets = None) -> bool:
    """
    Performs a quick validation of the probe's result `value` against the
    `tolerance` that was provided.

    The tolerance is typed and is therefore dispatched to the right function
    at runtime based on the `tolerance` type.

    Note that the `tolerance` maybe a dictionary, in which case it should
    follow the activity provider specification so that it can be called with
    the probe's result `value` as an argument, returning a success when the
    `value` is within range.
    """
    pass


@within_tolerance.register(bool)
def _(tolerance: bool, value: bool, configuration: Configuration = None,
      secrets: Secrets = None) -> bool:
    return value == tolerance


@within_tolerance.register(str)
def _(tolerance: str, value: str, configuration: Configuration = None,
      secrets: Secrets = None) -> bool:
    return value == tolerance


@within_tolerance.register(int)
def _(tolerance: int, value: int, configuration: Configuration = None,
      secrets: Secrets = None) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return value["status"] == tolerance

    return value == tolerance


@within_tolerance.register(list)
def _(tolerance: list, value: Any, configuration: Configuration = None,
      secrets: Secrets = None) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return value["status"] in tolerance

    if len(tolerance) == 2:
        return tolerance[0] <= value <= tolerance[1]

    return value in tolerance


@within_tolerance.register(dict)  #noqa: C901
def _(tolerance: dict, value: Any, configuration: Configuration = None,  #noqa: C901
      secrets: Secrets = None) -> bool:
    tolerance_type = tolerance.get("type")

    if tolerance_type == "probe":
        tolerance["provider"]["arguments"]["value"] = value
        try:
            rtn = run_activity(tolerance, configuration, secrets)
            if rtn:
                return True
            else:
                return False
        except ActivityFailed:
            return False
    elif tolerance_type == "regex":
        target = tolerance.get("target")
        pattern = tolerance.get("pattern")
        pattern = substitute(pattern, configuration, secrets)
        logger.debug("Applied pattern is: {}".format(pattern))
        rx = re.compile(pattern)
        if target:
            value = value.get(target, value)
        return rx.search(value) is not None
    elif tolerance_type == "jsonpath":
        target = tolerance.get("target")
        path = tolerance.get("path")
        count_value = tolerance.get("count", None)
        path = substitute(path, configuration, secrets)
        logger.debug("Applied jsonpath is: {}".format(path))
        px = JSONPath.parse_str(path)

        if target:
            # if no target was provided, we use the tested value as-is
            value = value.get(target, value)

        if isinstance(value, bytes):
            value = value.decode('utf-8')

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.decoder.JSONDecodeError:
                pass

        values = list(map(lambda m: m.current_value, px.match(value)))
        result = len(values) > 0
        if count_value is not None:
            result = len(values) == count_value

        expect = tolerance.get("expect")
        if "expect" in tolerance:
            if not isinstance(expect, list):
                result = values == [expect]
            else:
                result = values == expect

        if "expect" in tolerance and result is False:
            expect_one_of = tolerance.get("expect_one_of")
            if expect_one_of is not None:
                result = values == expect_one_of

        if result is False:
            if "expect" in tolerance and "expect_one_of" in tolerance:
                logger.debug(
                    "jsonpath found '{}' but expected '{}' or '{}'".format(
                        str(values), str(tolerance["expect"]),
                        str(tolerance["expect_one_of"])))
            elif "expect" in tolerance:
                logger.debug(
                    "jsonpath found '{}' but expected '{}'".format(
                        str(values), str(tolerance["expect"])))
            else:
                logger.debug("jsonpath found '{}'".format(str(values)))

        return result
    elif tolerance_type == "range":
        target = tolerance.get("target")
        if target:
            value = value.get(target, value)

        try:
            value = Decimal(value)
        except InvalidOperation:
            logger.debug("range check expects a number value")
            return False

        the_range = tolerance.get("range")
        min_value = the_range[0]
        max_value = the_range[1]
        return Decimal(min_value) <= value <= Decimal(max_value)
