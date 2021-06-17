# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os.path
import signal
import sys
import tempfile
import types

import pytest
import requests_mock
import yaml

from chaoslib.activity import run_activities
from chaoslib.exceptions import ActivityFailed, InvalidActivity, \
    InvalidExperiment, InterruptExecution
from chaoslib.experiment import ensure_experiment_is_valid, load_experiment, \
    run_experiment

from fixtures import config, experiments


def test_empty_experiment_is_invalid():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.EmptyExperiment)
    assert "an empty experiment is not an experiment" in str(exc.value)


def test_load_yaml():
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(b"""---
a: 12
""")
        f.seek(0)
        doc = load_experiment(f.name)
        assert "a" in doc
        assert doc["a"] == 12


def test_load_yml():
    with tempfile.NamedTemporaryFile(suffix=".yml") as f:
        f.write(b"""---
a: 12
""")
        f.seek(0)
        doc = load_experiment(f.name)
        assert "a" in doc
        assert doc["a"] == 12


def test_load_json():
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        f.write(json.dumps({"a": 12}).encode('utf-8'))
        f.seek(0)
        doc = load_experiment(f.name)
        assert "a" in doc
        assert doc["a"] == 12


def test_unknown_extension():
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        with pytest.raises(InvalidExperiment) as x:
            load_experiment(f.name)
        assert "json, yaml or yml extensions are supported" in str(x.value)


def test_experiment_must_have_a_method():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingMethodExperiment)
    assert "an experiment requires a method" in str(exc.value)


def test_experiment_method_without_steps():
    ensure_experiment_is_valid(experiments.NoStepsMethodExperiment)


def test_experiment_must_have_a_title():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingTitleExperiment)
    assert "experiment requires a title" in str(exc.value)


def test_experiment_title_substitution():
    journal = run_experiment(experiments.ExperimentWithInterpolatedTitle)

    assert journal["experiment"]["title"] in "Cats in space: do cats live in the Internet?"


def test_experiment_must_have_a_description():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingDescriptionExperiment)
    assert "experiment requires a description" in str(exc.value)


def test_experiment_may_not_have_a_hypothesis():
    assert ensure_experiment_is_valid(
        experiments.MissingHypothesisExperiment) is None


def test_experiment_hypothesis_must_have_a_title():
    with pytest.raises(InvalidExperiment) as exc:
        ensure_experiment_is_valid(experiments.MissingHypothesisTitleExperiment)
    assert "hypothesis requires a title" in str(exc.value)


def test_experiment_hypothesis_must_have_a_valid_probe():
    with pytest.raises(InvalidActivity) as exc:
        ensure_experiment_is_valid(experiments.ExperimentWithInvalidHypoProbe)
    assert "required argument 'path' is missing from activity" in str(exc.value)


def test_valid_experiment():
    assert ensure_experiment_is_valid(experiments.Experiment) is None


def test_valid_experiment_from_json():
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        f.write(json.dumps(experiments.Experiment).encode('utf-8'))
        f.seek(0)
        doc = load_experiment(f.name)
        assert ensure_experiment_is_valid(doc) is None


def test_valid_experiment_from_yaml():
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(yaml.dump(experiments.Experiment).encode('utf-8'))
        f.seek(0)
        doc = load_experiment(f.name)
        assert ensure_experiment_is_valid(doc) is None


def test_can_run_experiment_in_dry_mode():
    experiment = experiments.Experiment.copy()
    experiment["dry"] = True

    journal = run_experiment(experiment)
    assert isinstance(journal, dict)


def test_can_run_experiment_with_activity_in_dry_mode():
    experiment = experiments.ExperimentWithBypassedActivity.copy()
    journal = run_experiment(experiment)
    assert isinstance(journal, dict)
    assert journal["run"][0]["output"] == None


def test_can_iterate_over_activities():
    g = run_activities(
        experiments.Experiment, configuration=None, secrets=None, pool=None,
        dry=False)
    assert isinstance(g, types.GeneratorType)


def test_no_rollback_even_on_SIGINT():
    def handler(signum, frame):
        raise KeyboardInterrupt()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        journal = run_experiment(experiments.ExperimentWithLongPause)
        assert isinstance(journal, dict)
        assert journal["status"] == "interrupted"
    except KeyboardInterrupt:
        pytest.fail("we should have swallowed the KeyboardInterrupt exception")


def test_no_rollback_even_on_SystemExit():
    def handler(signum, frame):
        raise SystemExit()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        journal = run_experiment(experiments.ExperimentWithLongPause)
        assert isinstance(journal, dict)
        assert journal["status"] == "interrupted"
    except SystemExit:
        pytest.fail("we should have swallowed the SystemExit exception")


def test_can_interrupt_rollbacks():
    def handler(signum, frame):
        raise InterruptExecution("boom")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        journal = run_experiment(experiments.ExperimentWithRollbackLongPause)
        assert isinstance(journal, dict)
        assert journal["status"] == "interrupted"
    except Exception:
        pytest.fail("we should have swallowed the InterruptExecution exception")


def test_can_interrupt_rollbacks_on_SystemExit():
    def handler(signum, frame):
        raise SystemExit()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        journal = run_experiment(experiments.ExperimentWithRollbackLongPause)
        assert isinstance(journal, dict)
        assert journal["status"] == "interrupted"
    except SystemExit:
        pytest.fail("we should have swallowed the SystemExit exception")


def test_can_interrupt_rollbacks_on_SIGINT():
    def handler(signum, frame):
        raise KeyboardInterrupt()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        journal = run_experiment(experiments.ExperimentWithRollbackLongPause)
        assert isinstance(journal, dict)
        assert journal["status"] == "interrupted"
    except SystemExit:
        pytest.fail("we should have swallowed the KeyboardInterrupt exception")


def test_probes_can_reference_each_other():
    experiment = experiments.RefProbeExperiment.copy()
    experiment["dry"] = True

    try:
        run_experiment(experiment)
    except:
        pytest.fail("experiment should not have failed")


def test_probes_missing_ref_should_fail_the_experiment():
    experiment = experiments.MissingRefProbeExperiment.copy()
    experiment["dry"] = True

    journal = run_experiment(experiment)
    assert journal["status"] == "aborted"


def test_experiment_with_steady_state():
    with requests_mock.mock() as m:
        m.get('http://example.com', status_code=200)
        journal = run_experiment(experiments.HTTPToleranceExperiment)
        assert isinstance(journal, dict)
        assert journal["status"] == "completed"

    with requests_mock.mock() as m:
        m.get('http://example.com', status_code=404)
        journal = run_experiment(experiments.HTTPToleranceExperiment)
        assert isinstance(journal, dict)
        assert journal["status"] == "failed"


def test_experiment_with_failing_steady_state():
    with requests_mock.mock() as m:
        m.get('http://example.com', status_code=500)
        journal = run_experiment(experiments.Experiment)
        assert isinstance(journal, dict)
        assert journal["status"] == "failed"
        assert len(journal["rollbacks"]) == 0


def test_experiment_may_run_without_steady_state():
    experiment = experiments.Experiment.copy()
    experiment.pop("steady-state-hypothesis")
    experiment["dry"] = True

    journal = run_experiment(experiment)
    assert journal is not None


def test_should_bail_experiment_when_env_was_not_found():
    experiment = experiments.ExperimentWithConfigurationCallingMissingEnvKey

    with pytest.raises(InvalidExperiment) as x:
        run_experiment(experiment)
    assert "Configuration makes reference to an environment key that does " \
           "not exist" in str(x.value)


def test_validate_all_tolerance_probes():
    with requests_mock.mock() as m:
        m.get("http://example.com", text="you are number 87")

        ensure_experiment_is_valid(experiments.ExperimentWithVariousTolerances)


def test_dry_run_should_not_pause_after():
    experiment = experiments.ExperimentWithLongPause.copy()
    experiment["dry"] = True

    start = datetime.utcnow()
    run_experiment(experiment)
    end = datetime.utcnow()

    experiment_run_time = int((end - start).total_seconds())
    pause_after_duration = int(experiment["method"][1]["pauses"]["after"])

    assert experiment_run_time < pause_after_duration


def test_actionless_run_should_not_pause_after():
    experiment = experiments.ExperimentWithLongPauseAction.copy()
    experiment["actionless"] = True

    start = datetime.utcnow()
    run_experiment(experiment)
    end = datetime.utcnow()

    experiment_run_time = int((end - start).total_seconds())
    pause_after_duration = int(experiment["method"][1]["pauses"]["after"])

    assert experiment_run_time < pause_after_duration


def test_dry_run_should_not_pause_before():
    experiment = experiments.ExperimentWithLongPauseBefore.copy()
    experiment["dry"] = True

    start = datetime.utcnow()
    run_experiment(experiment)
    end = datetime.utcnow()

    experiment_run_time = int((end - start).total_seconds())
    pause_before_duration = int(experiment["method"][1]["pauses"]["before"])

    assert experiment_run_time < pause_before_duration


def test_actionless_run_should_not_pause_before():
    experiment = experiments.ExperimentWithLongPauseAction.copy()
    experiment["actionless"] = True

    start = datetime.utcnow()
    run_experiment(experiment)
    end = datetime.utcnow()

    experiment_run_time = int((end - start).total_seconds())
    pause_before_duration = int(experiment["method"][1]["pauses"]["before"])

    assert experiment_run_time < pause_before_duration


def test_rollback_default_strategy_does_not_run_on_failed_activity_in_ssh():
    experiment = experiments.ExperimentWithFailedActionInSSHAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "default"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "failed"
    assert len(journal["rollbacks"]) == 0


def test_rollback_default_strategy_runs_on_failed_activity_in_method():
    experiment = experiments.ExperimentWithFailedActionInMethodAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "default"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "completed"
    assert len(journal["rollbacks"]) == 1


def test_rollback_default_strategy_does_not_run_on_interrupted_experiment_in_method():
    experiment = experiments.ExperimentWithInterruptedExperimentAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "always"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "interrupted"
    assert len(journal["rollbacks"]) == 1


def test_rollback_always_strategy_runs_on_failed_activity_in_ssh():
    experiment = experiments.ExperimentWithFailedActionInSSHAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "always"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "failed"
    assert len(journal["rollbacks"]) == 1


def test_rollback_always_strategy_runs_on_interrupted_experiment_in_method():
    experiment = experiments.ExperimentWithInterruptedExperimentAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "always"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "interrupted"
    assert len(journal["rollbacks"]) == 1


def test_rollback_always_strategy_runs_on_failed_activity_in_method():
    experiment = experiments.ExperimentWithFailedActionInMethodAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "always"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "completed"
    assert len(journal["rollbacks"]) == 1


def test_rollback_never_strategy_does_not_run_on_failed_activity_in_ssh():
    experiment = experiments.ExperimentWithFailedActionInSSHAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "never"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "failed"
    assert len(journal["rollbacks"]) == 0


def test_rollback_never_strategy_does_not_run_on_interrupted_experiment_in_method():
    experiment = experiments.ExperimentWithInterruptedExperimentAndARollback
    #experiment["dry"] = True
    settings = {
        "runtime": {
            "rollbacks": {
                "strategy": "never"
            }
        }
    }

    journal = run_experiment(experiment, settings)
    assert journal["status"] == "interrupted"
    assert len(journal["rollbacks"]) == 0


def test_can_run_experiment_in_actionless_mode():
    experiment = experiments.ExperimentWithLongPauseAction.copy()
    experiment["actionless"] = True

    journal = run_experiment(experiment)
    assert isinstance(journal, dict)
