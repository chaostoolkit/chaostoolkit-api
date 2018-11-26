# -*- coding: utf-8 -*-
from contextlib import contextmanager
from copy import deepcopy
from functools import wraps
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Generator, List, NoReturn, Union

from logzero import logger

from chaoslib.control.python import apply_python_control, cleanup_control, \
    initialize_control, validate_python_control
from chaoslib.exceptions import ActivityFailed, InterruptExecution, \
    InvalidExperiment, InvalidActivity, ControlPythonFunctionLoadingError, \
    InvalidControl
from chaoslib.types import Activity, Configuration, Control, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings

__all__ = ["controls", "initialize_controls", "cleanup_controls",
           "validate_controls", "Control"]


def initialize_controls(experiment: Experiment,
                        configuration: Configuration = None,
                        secrets: Secrets = None):
    """
    Initialize all declared controls in the experiment.

    On Python controls, this means calling the `configure_control` function
    of the exposed module.

    Controls are initialized once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Initializing controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug("Initializing control '{}'".format(name))

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            initialize_control(control, configuration, secrets)


def cleanup_controls(experiment: Experiment):
    """
    Cleanup all declared controls in the experiment.

    On Python controls, this means calling the `cleanup_control` function
    of the exposed module.

    Controls are cleaned up once only when they are declared many
    times in the experiment with the same name.
    """
    logger.debug("Cleaning up controls")
    controls = get_controls(experiment)

    seen = []
    for control in controls:
        name = control.get("name")
        if not name or name in seen:
            continue
        seen.append(name)
        logger.debug("Cleaning up control '{}'".format(name))

        provider = control.get("provider")
        if provider and provider["type"] == "python":
            cleanup_control(control)


def validate_controls(experiment: Experiment):
    """
    Validate that all declared controls respect the specification.

    Raises :exc:`chaoslib.exceptions.InvalidControl` when they are not valid.
    """
    references = [
        c["name"] for c in get_controls(experiment) if "ref" not in c
    ]
    for c in get_controls(experiment):
        if "ref" in c:
            if c["ref"] not in references:
                raise InvalidControl(
                    "Control reference '{}' declaration cannot be found")

    for control in get_controls(experiment):
        provider_type = control.get("provider", {}).get("type")
        if provider_type == "python":
            validate_python_control(control)


class Control:
    def begin(self, level: str, experiment: Experiment,
              context: Union[Activity, Hypothesis, Experiment],
              configuration: Configuration = None, secrets: Secrets = None):
        self.state = None
        apply_controls(
            level=level, experiment=experiment, context=context,
            scope="pre", configuration=configuration, secrets=secrets)

    def with_state(self, state):
        self.state = state

    def end(self, level: str, experiment: Experiment,
            context: Union[Activity, Hypothesis, Experiment],
            configuration: Configuration = None, secrets: Secrets = None):
        state = self.state
        self.state = None
        apply_controls(
            level=level, experiment=experiment, context=context,
            scope="post", state=state, configuration=configuration,
            secrets=secrets)


@contextmanager
def controls(level: str, experiment: Experiment,
             context: Union[Activity, Hypothesis, Experiment],
             configuration: Configuration = None, secrets: Secrets = None):
    """
    Context manager for a block that needs to be wrapped by controls.
    """
    try:
        c = Control()
        c.begin(level, experiment, context, configuration, secrets)
        yield c
    finally:
        c.end(level, experiment, context, configuration, secrets)


###############################################################################
# Internals
###############################################################################
def get_all_activities(experiment: Experiment) -> List[Activity]:
    activities = []
    activities.extend(
        experiment.get("steady-state-hypothesis", {}).get("probes", []))
    activities.extend(
        experiment.get("method", []))
    activities.extend(
        experiment.get("rollbacks", []))
    return activities


def get_controls(experiment: Experiment) -> List[Control]:
    controls = []
    controls.extend(experiment.get("controls", []))
    controls.extend(
        experiment.get("steady-state-hypothesis", {}).get("controls", []))

    for activity in get_all_activities(experiment):
        controls.extend(activity.get("controls", []))
    return controls


def get_context_controls(experiment: Experiment,
                         context: Union[Activity, Experiment]) \
                         -> List[Control]:
    """
    Get the controls at the given level by merging those declared at the
    experiment level with the current's context.

    If a control is declared at the current level, do override it with an
    top-level ine.
    """
    top_level_controls = experiment.get("controls", [])

    controls = context.get("controls", [])
    if not controls and not top_level_controls:
        return []
    elif not controls and top_level_controls:
        return [
            deepcopy(c)
            for c in top_level_controls
            if c.get("automatic", True)
        ]

    for c in controls.copy():
        if "ref" in c:
            for top_level_control in top_level_controls:
                if c["ref"] == top_level_control["name"]:
                    controls.append(deepcopy(top_level_control))
                    break
        else:
            for tc in top_level_controls:
                if c.get("name") == tc.get("name"):
                    break

                if tc.get("automatic", True):
                    controls.append(deepcopy(tc))

    return controls


def apply_controls(level: str, experiment: Experiment,
                   context: Union[Activity, Hypothesis, Experiment],
                   scope: str, state: Union[Journal, Run, List[Run]] = None,
                   configuration: Configuration = None,
                   secrets: Secrets = None):
    """
    Apply the controls at given level

    The ̀ level` parameter is one of `"experiment", "hypothesis", "method",
    "rollback", "activity"`. The `context` is usually an experiment except at
    the `"activity"` when it must be an activity. The `scope` is one of
    `"pre", "post"` and the `state` is only set on `"post"` scope.
    """
    controls = get_context_controls(experiment, context)
    if not controls:
        return

    for control in controls:
        control_name = control.get("name")
        target_scope = control.get("scope")
        if not target_scope:
            continue

        if not isinstance(target_scope, list):
            target_scope = [target_scope]

        if scope not in target_scope:
            continue

        logger.debug(
            "Applying {}-control '{}' on '{}'".format(
                scope, control_name, level))
        provider = control.get("provider", {})
        provider_type = provider.get("type")

        try:
            if provider_type == "python":
                level = "{}-{}".format(level, scope)
                apply_python_control(
                    level=level, control=control, context=context, state=state,
                    configuration=configuration, secrets=secrets)
        except InterruptExecution as c:
            logger.debug(
                "{}-control '{}' interrupted the execution".format(
                    scope.title(), control_name), exc_info=True)
            raise
        except Exception as x:
            logger.debug(
                "{}-control '{}' failed".format(
                    scope.title(), control_name), exc_info=True)
