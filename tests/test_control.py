# -*- coding: utf-8 -*-
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import os
import tempfile
from typing import Any, Dict, List
from unittest.mock import patch

from pkg_resources import Distribution, EntryPoint, working_set
import logzero
import pytest

from chaoslib.activity import execute_activity
from chaoslib.control import initialize_controls, cleanup_controls, \
    validate_controls, controls, get_all_activities, get_context_controls, \
    initialize_global_controls, cleanup_global_controls, get_global_controls
from chaoslib.control.python import validate_python_control
from chaoslib.exceptions import InterruptExecution, InvalidActivity
from chaoslib.experiment import run_experiment
from chaoslib.types import Activity, Configuration, Control, \
    Experiment, Hypothesis, Journal, Run, Secrets,  Settings

from fixtures import  experiments
from fixtures.controls import dummy as DummyControl


def test_initialize_controls_will_configure_a_control():
    exp = deepcopy(experiments.ExperimentWithControls)
    initialize_controls(
        exp, configuration={
            "dummy-key": "dummy-value"
        })
    assert exp["control-value"] == "dummy-value"
    cleanup_controls(exp)


def test_initialize_controls_will_cleanup_a_control():
    exp = deepcopy(experiments.ExperimentWithControls)
    cleanup_controls(exp)


def test_controls_are_applied_before_and_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("experiment", exp, context=exp):
        assert "before_experiment_control" in exp
        assert exp["before_experiment_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" in exp
    assert exp["after_experiment_control"] is True
    assert journal["after_experiment_control"] is True


def test_controls_are_applied_before_and_but_not_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = "before"
    with controls("experiment", exp, context=exp):
        assert "before_experiment_control" in exp
        assert exp["before_experiment_control"] is True

        exp["dry"] = True
        run_experiment(exp)

    assert "after_experiment_control" not in exp


def test_controls_are_applied_not_before_and_but_after_experiment():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["scope"] = "after"
    with controls("experiment", exp, context=exp):
        assert "before_experiment_control" not in exp

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_experiment_control" in exp
    assert exp["after_experiment_control"] is True
    assert journal["after_experiment_control"] is True


def test_controls_may_interrupt_experiment():
    exp = deepcopy(experiments.ExperimentCanBeInterruptedByControl)
    with controls("experiment", exp, context=exp):
        exp["dry"] = True
        journal = run_experiment(exp)
        assert journal["status"] == "interrupted"


def test_controls_are_applied_before_and_after_hypothesis():
    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    with controls("hypothesis", exp, context=hypo):
        assert "before_hypothesis_control" in hypo
        assert hypo["before_hypothesis_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_hypothesis_control" in hypo
    assert hypo["after_hypothesis_control"] is True
    assert journal["steady_states"]["before"]["after_hypothesis_control"] is True


def test_controls_are_applied_before_and_after_method():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("method", exp, context=exp):
        assert "before_method_control" in exp
        assert exp["before_method_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_method_control" in exp
    assert exp["after_method_control"] is True
    assert "after_method_control" in journal["run"]


def test_controls_are_applied_before_and_after_rollbacks():
    exp = deepcopy(experiments.ExperimentWithControls)
    with controls("rollback", exp, context=exp):
        assert "before_rollback_control" in exp
        assert exp["before_rollback_control"] is True

        exp["dry"] = True
        journal = run_experiment(exp)

    assert "after_rollback_control" in exp
    assert exp["after_rollback_control"] is True
    assert "after_rollback_control" in journal["rollbacks"]


def test_controls_are_applied_before_and_after_activities():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["dry"] = True

    activities = get_all_activities(exp)
    for activity in activities:
        with controls("activity", exp, context=activity):
            assert activity["before_activity_control"] is True

            run = execute_activity(exp, activity, None, None, dry=False)

            assert "after_activity_control" in activity
            assert activity["after_activity_control"] is True
            assert run["after_activity_control"] is True


def test_no_controls_get_applied_when_none_defined():
    exp = deepcopy(experiments.ExperimentWithoutControls)
    exp["dry"] = True

    with controls("experiment", exp, context=exp):
        assert "before_experiment_control" not in exp

        exp["dry"] = True
        run_experiment(exp)

    assert "after_experiment_control" not in exp


def test_automatic_goes_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)

    controls = get_context_controls("experiment", exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls("hypothesis", exp, hypo)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls("activity", exp, activity)
        assert len(controls) == 1


def test_not_automatic_does_not_go_deep_down_the_tree():
    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False

    controls = get_context_controls("experiment", exp, exp)
    assert len(controls) == 1

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    hypo = exp["steady-state-hypothesis"]
    assert "controls" not in hypo
    controls = get_context_controls("hypothesis", exp, hypo)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    controls = get_context_controls("method", exp, exp)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    controls = get_context_controls("rollback", exp, exp)
    assert len(controls) == 0

    exp = deepcopy(experiments.ExperimentWithControls)
    exp["controls"][0]["automatic"] = False
    activities = get_all_activities(exp)
    for activity in activities:
        assert "controls" not in activity
        controls = get_context_controls("activity", exp, activity)
        assert len(controls) == 0


@patch('chaoslib.control.python.logger', autospec=True)
def test_validate_python_control_must_be_loadable(logger):
    validate_python_control({
        "name": "a-python-control",
        "provider": {
            "type": "python",
            "module": "blah.blah"
        }
    })
    args = logger.warning.call_args
    msg = "Could not find Python module 'blah.blah' in control " \
        "'a-python-control'. Did you install the Python module?"
    assert msg in args[0][0]


def test_validate_python_control_needs_a_module():
    with pytest.raises(InvalidActivity):
        validate_python_control({
            "name": "a-python-control",
            "provider": {
                "type": "python"
            }
        })


def test_controls_can_access_experiment():
    exp = deepcopy(experiments.ExperimentWithControlAccessingExperiment)
    exp["dry"] = True

    hypo = exp.get("steady-state-hypothesis")
    run_experiment(exp)
    assert hypo["has_experiment_before"] is True
    assert hypo["has_experiment_after"] is True

    activities = get_all_activities(exp)
    for activity in activities:
        assert activity["has_experiment_before"] is True
        assert activity["has_experiment_after"] is True


def test_controls_are_applied_at_various_levels():
    exp = deepcopy(experiments.ExperimentWithControlsAtVariousLevels)
    exp["dry"] = True

    run_experiment(exp)
    activities = get_all_activities(exp)
    for activity in activities:
        if "controls" in activity:
            assert activity["before_activity_control"] is True
            assert activity["after_activity_control"] is True


def test_controls_are_applied_when_they_are_not_top_level():
    exp = deepcopy(experiments.ExperimentWithControlNotAtTopLevel)
    exp["dry"] = True

    run_experiment(exp)
    activities = get_all_activities(exp)
    for activity in activities:
        if "controls" in activity:
            assert activity["before_activity_control"] is True
            assert activity["after_activity_control"] is True


def test_load_global_controls_from_settings():
    exp = deepcopy(experiments.ExperimentNoControls)
    activities = get_all_activities(exp)

    for activity in activities:
        assert "before_activity_control" not in activity
        assert "after_activity_control" not in activity

    assert get_global_controls() == []
    run_experiment(exp, settings={
        "dummy-key": "hello there",
        "controls": {
            "dummy": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy"
                }
            }
        }
    })
    assert get_global_controls() == []
    assert exp["control-value"] == "hello there"

    for activity in activities:
        assert "before_activity_control" in activity
        assert "after_activity_control" in activity
        assert activity["before_activity_control"] is True
        assert activity["after_activity_control"] is True


def test_get_globally_loaded_controls_from_settings():
    assert get_global_controls() == []

    initialize_global_controls({}, {}, {}, {
        "controls": {
            "dummy": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy"
                }
            }
        }
    })

    try:
        ctrls = get_global_controls()
        assert len(ctrls) == 1
        assert ctrls[0]["name"] == "dummy"
        assert ctrls[0]["provider"]["type"] == "python"
        assert ctrls[0]["provider"]["module"] == "fixtures.controls.dummy"
    finally:
        cleanup_global_controls()
        assert get_global_controls() == []


def test_load_global_controls_from_settings_configured_via_exp_config():
    exp = deepcopy(experiments.ExperimentUsingConfigToConfigureControls)
    activities = get_all_activities(exp)

    for activity in activities:
        assert "before_activity_control" not in activity
        assert "after_activity_control" not in activity

    assert get_global_controls() == []
    run_experiment(exp, settings={
        "controls": {
            "dummy": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy"
                }
            }
        }
    })
    assert get_global_controls() == []
    assert exp["control-value"] == "blah blah"

    for activity in activities:
        assert "before_activity_control" in activity
        assert "after_activity_control" in activity
        assert activity["before_activity_control"] is True
        assert activity["after_activity_control"] is True


def test_apply_controls_even_on_background_activity():
    exp = deepcopy(experiments.ExperimentNoControls)
    exp["method"][0]["background"] = True
    exp["method"][0]["pauses"] = {
        "after": 1
    }
    activities = get_all_activities(exp)

    for activity in activities:
        assert "before_activity_control" not in activity
        assert "after_activity_control" not in activity

    assert get_global_controls() == []
    run_experiment(exp, settings={
        "dummy-key": "hello there",
        "controls": {
            "dummy": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy"
                }
            }
        }
    })
    assert get_global_controls() == []
    assert exp["control-value"] == "hello there"

    for activity in activities:
        assert "before_activity_control" in activity
        assert "after_activity_control" in activity
        assert activity["before_activity_control"] is True
        assert activity["after_activity_control"] is True


def test_control_cleanup_cannot_fail_the_experiment():
    exp = deepcopy(experiments.ExperimentNoControls)
    try:
        run_experiment(exp, settings={
            "dummy-key": "hello there",
            "controls": {
                "dummy": {
                    "provider": {
                        "type": "python",
                        "module": "fixtures.controls.dummy_with_failing_cleanup"
                    }
                }
            }
        })
    except:
        pytest.fail("Failed to run experiment with a broken cleanup control")


def test_control_initialization_cannot_fail_the_experiment():
    exp = deepcopy(experiments.ExperimentNoControls)
    try:
        run_experiment(exp, settings={
            "dummy-key": "hello there",
            "controls": {
                "dummy": {
                    "provider": {
                        "type": "python",
                        "module": "fixtures.controls.dummy_with_failing_init"
                    }
                }
            }
        })
    except:
        pytest.fail("Failed to run experiment with a broken init control")


def test_control_failing_its_initialization_must_not_be_registered():
    exp = deepcopy(experiments.ExperimentNoControls)
    run_experiment(exp, settings={
        "dummy-key": "hello there",
        "controls": {
            "dummy-failed": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy_with_failing_init"
                }
            },
            "dummy": {
                "provider": {
                    "type": "python",
                    "module": "fixtures.controls.dummy"
                }
            }
        }
    })

    assert "should_never_been_called" not in exp

    activities = get_all_activities(exp)
    for activity in activities:
        assert "before_activity_control" in activity
        assert "after_activity_control" in activity
        assert activity["before_activity_control"] is True
        assert activity["after_activity_control"] is True
