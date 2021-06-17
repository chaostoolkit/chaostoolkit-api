# -*- coding: utf-8 -*-
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
try:
    import ctypes
    HAS_CTYPES = True
except ImportError:
    HAS_CTYPES = False
from datetime import datetime
import platform
import threading
import time
from typing import Any, Dict, List, Optional

from logzero import logger

from chaoslib import __version__, substitute
from chaoslib.activity import run_activities
from chaoslib.control import initialize_controls, controls, cleanup_controls, \
    Control, initialize_global_controls, cleanup_global_controls
from chaoslib.exceptions import ChaosException, ExperimentExitedException, \
    InterruptExecution
from chaoslib.exit import exit_signals
from chaoslib.configuration import load_configuration
from chaoslib.hypothesis import run_steady_state_hypothesis
from chaoslib.rollback import run_rollbacks
from chaoslib.secret import load_secrets
from chaoslib.settings import get_loaded_settings
from chaoslib.types import Configuration, Experiment, Journal, Run, Secrets, \
    Settings, Schedule, Strategy

__all__ = ["Runner", "RunEventHandler"]


class RunEventHandler:
    """
    Base class to react to certain, or all, events during an execution.

    This is mainly meant for reacting the execution's mainloop. Do not
    implement it as part of an extension, use the Control interface instead.
    """
    def started(self, experiment: Experiment, journal: Journal) -> None:
        logger.debug("Experiment execution started")

    def finish(self, journal: Journal) -> None:
        logger.debug("Experiment execution finished")

    def interrupted(self, experiment: Experiment,
                    journal: Journal) -> None:
        logger.debug("Experiment execution was interrupted by a control")

    def signal_exit(self) -> None:
        logger.debug("Experiment execution caught a system signal")

    def start_continous_hypothesis(self, frequency: int) -> None:
        logger.debug("Steady state will run continously now")

    def continous_hypothesis_iteration(self, iteration_index: int,
                                       state: Any) -> None:
        logger.debug("Steady state iteration {}".format(iteration_index))

    def continous_hypothesis_completed(self, experiment: Experiment,
                                       journal: Journal,
                                       exception: Exception = None) \
                                           -> None:
        logger.debug("Continous steady state is now complete")

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        logger.debug("Steady state hypothesis is now running before method")

    def hypothesis_before_completed(self, experiment: Experiment,
                                    state: Dict[str, Any],
                                    journal: Journal) -> None:
        logger.debug("Steady state hypothesis before method completed")

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        logger.debug("Steady state hypothesis is now running after method")

    def hypothesis_after_completed(self, experiment: Experiment,
                                   state: Dict[str, Any],
                                   journal: Journal) -> None:
        logger.debug("Steady state hypothesis after method completed")

    def start_method(self, experiment: Experiment) -> None:
        logger.debug("Method has now started")

    def method_completed(self, experiment: Experiment, state: Any) -> None:
        logger.debug("Method has now completed")

    def start_rollbacks(self, experiment: Experiment) -> None:
        logger.debug("Rollbacks have now started")

    def rollbacks_completed(self, experiment: Experiment,
                            journal: Journal) -> None:
        logger.debug("Rollbacks have now completed")

    def start_cooldown(self, duration: int) -> None:
        logger.debug("Cooldown period has now started")

    def cooldown_completed(self) -> None:
        logger.debug("Cooldown period has now completed")


class EventHandlerRegistry:
    def __init__(self):
        self.handlers = []

    def register(self, handler: RunEventHandler) -> None:
        self.handlers.append(handler)

    def started(self, experiment: Experiment, journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.started(experiment, journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def finish(self, journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.finish(journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def interrupted(self, experiment: Experiment,
                    journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.interrupted(experiment, journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def signal_exit(self) -> None:
        for h in self.handlers:
            try:
                h.signal_exit()
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_continous_hypothesis(self, frequency: int) -> None:
        for h in self.handlers:
            try:
                h.start_continous_hypothesis(frequency)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def continous_hypothesis_iteration(self, iteration_index: int,
                                       state: Any) -> None:
        for h in self.handlers:
            try:
                h.continous_hypothesis_iteration(iteration_index, state)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def continous_hypothesis_completed(self, experiment: Experiment,
                                       journal: Journal,
                                       exception: Exception = None) \
                                           -> None:
        for h in self.handlers:
            try:
                h.continous_hypothesis_completed(
                    experiment, journal, exception)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        for h in self.handlers:
            try:
                h.start_hypothesis_before(experiment)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def hypothesis_before_completed(self, experiment: Experiment,
                                    state: Dict[str, Any],
                                    journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.hypothesis_before_completed(experiment, state, journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        for h in self.handlers:
            try:
                h.start_hypothesis_after(experiment)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def hypothesis_after_completed(self, experiment: Experiment,
                                   state: Dict[str, Any],
                                   journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.hypothesis_after_completed(experiment, state, journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_method(self, experiment: Experiment) -> None:
        for h in self.handlers:
            try:
                h.start_method(experiment)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def method_completed(self, experiment: Experiment,
                         state: Any = None) -> None:
        for h in self.handlers:
            try:
                h.method_completed(experiment, state)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_rollbacks(self, experiment: Experiment) -> None:
        for h in self.handlers:
            try:
                h.start_rollbacks(experiment)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def rollbacks_completed(self, experiment: Experiment,
                            journal: Journal) -> None:
        for h in self.handlers:
            try:
                h.rollbacks_completed(experiment, journal)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def start_cooldown(self, duration: int) -> None:
        for h in self.handlers:
            try:
                h.start_cooldown(duration)
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)

    def cooldown_completed(self) -> None:
        for h in self.handlers:
            try:
                h.cooldown_completed()
            except Exception:
                logger.debug(
                    "Handler {} failed".format(
                        h.__class__.__name__), exc_info=True)


class Runner:
    def __init__(self, strategy: Strategy, schedule: Schedule = None):
        self.strategy = strategy
        self.schedule = schedule or Schedule()
        self.event_registry = EventHandlerRegistry()

    def __enter__(self) -> 'Runner':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, tb: Any) -> None:
        self.cleanup()

    def register_event_handler(self, handler: RunEventHandler) -> None:
        self.event_registry.register(handler)

    def configure(self, experiment: Experiment,
                  settings: Settings, experiment_vars: Dict[str, Any]) -> None:
        config_vars, secret_vars = experiment_vars or (None, None)
        self.settings = settings if settings is not None else \
            get_loaded_settings()
        self.config = load_configuration(
            experiment.get("configuration", {}), config_vars)
        self.secrets = load_secrets(
            experiment.get("secrets", {}), self.config, secret_vars)

    def cleanup(self):
        pass

    def run(self, experiment: Experiment,
            settings: Settings = None, experiment_vars: Dict[str, Any] = None,
            journal: Journal = None) -> Journal:

        self.configure(experiment, settings, experiment_vars)
        with exit_signals():
            journal = self._run(
                self.strategy, self.schedule, experiment, journal,
                self.config, self.secrets, self.settings,
                self.event_registry)
        return journal

    def _run(self, strategy: Strategy, schedule: Schedule,  # noqa: C901
             experiment: Experiment, journal: Journal,
             configuration: Configuration, secrets: Secrets,
             settings: Settings,
             event_registry: EventHandlerRegistry) -> None:
        experiment["title"] = substitute(
            experiment["title"], configuration, secrets)
        logger.info("Running experiment: {t}".format(t=experiment["title"]))

        started_at = time.time()
        journal = journal or initialize_run_journal(experiment)
        event_registry.started(experiment, journal)

        control = Control()
        activity_pool, rollback_pool = get_background_pools(experiment)
        hypo_pool = get_hypothesis_pool()
        continous_hypo_event = threading.Event()

        dry = experiment.get("dry", False)
        if dry:
            logger.warning("Dry mode enabled")

        actionless = experiment.get("actionless", False)
        if actionless:
            logger.warning("Actionless mode enabled")

        initialize_global_controls(
            experiment, configuration, secrets, settings)
        initialize_controls(experiment, configuration, secrets)

        logger.info("Steady-state strategy: {}".format(strategy.value))
        rollback_strategy = settings.get("runtime", {}).get(
            "rollbacks", {}).get("strategy", "default")
        logger.info("Rollbacks strategy: {}".format(rollback_strategy))

        exit_gracefully_with_rollbacks = True
        with_ssh = has_steady_state_hypothesis_with_probes(experiment)
        if not with_ssh:
            logger.info(
                "No steady state hypothesis defined. That's ok, just "
                "exploring.")

        try:
            try:
                control.begin(
                    "experiment", experiment, experiment, configuration,
                    secrets)

                state = object()
                if with_ssh and should_run_before_method(strategy):
                    state = run_gate_hypothesis(
                        experiment, journal, configuration, secrets,
                        event_registry, dry)

                if state is not None:
                    if with_ssh and should_run_during_method(strategy):
                        run_hypothesis_during_method(
                            hypo_pool, continous_hypo_event, strategy,
                            schedule, experiment, journal, configuration,
                            secrets, event_registry, dry)

                    state = run_method(
                            strategy, activity_pool, experiment, journal,
                            configuration, secrets, event_registry, dry,
                            actionless)

                    continous_hypo_event.set()
                    if journal["status"] not in ["interrupted", "aborted"]:
                        if with_ssh and (state is not None) and \
                                should_run_after_method(strategy):
                            run_deviation_validation_hypothesis(
                                experiment, journal, configuration, secrets,
                                event_registry, dry)
            except InterruptExecution as i:
                journal["status"] = "interrupted"
                logger.fatal(str(i))
                event_registry.interrupted(experiment, journal)
            except KeyboardInterrupt:
                journal["status"] = "interrupted"
                logger.warning("Received a termination signal (Ctrl-C)...")
                event_registry.signal_exit()
            except SystemExit as x:
                journal["status"] = "interrupted"
                logger.warning("Received the exit signal: {}".format(x.code))

                exit_gracefully_with_rollbacks = x.code != 30
                if not exit_gracefully_with_rollbacks:
                    logger.warning("Ignoring rollbacks as per signal")
                event_registry.signal_exit()
            finally:
                hypo_pool.shutdown(wait=True)

            # just in case a signal overrode everything else to tell us not to
            # play them anyway (see the exit.py module)
            if exit_gracefully_with_rollbacks:
                run_rollback(
                    rollback_strategy, rollback_pool, experiment, journal,
                    configuration, secrets, event_registry, dry, actionless)

            journal["end"] = datetime.utcnow().isoformat()
            journal["duration"] = time.time() - started_at

            # the spec only allows these statuses, so if it's anything else
            # we override to "completed"
            if journal["status"] not in (
                    "completed", "failed", "aborted", "interrupted"):
                journal["status"] = "completed"

            has_deviated = journal["deviated"]
            status = "deviated" if has_deviated else journal["status"]
            logger.info("Experiment ended with status: {s}".format(s=status))
            if has_deviated:
                logger.info(
                    "The steady-state has deviated, a weakness may have been "
                    "discovered")

            control.with_state(journal)
            try:
                control.end(
                    "experiment", experiment, experiment, configuration,
                    secrets)
            except ChaosException:
                logger.debug("Failed to close controls", exc_info=True)
        finally:
            try:
                cleanup_controls(experiment)
                cleanup_global_controls()
            finally:
                event_registry.finish(journal)

        return journal


def should_run_before_method(strategy: Strategy) -> bool:
    return strategy in [
        Strategy.BEFORE_METHOD, Strategy.DEFAULT, Strategy.CONTINOUS]


def should_run_after_method(strategy: Strategy) -> bool:
    return strategy in [
        Strategy.AFTER_METHOD, Strategy.DEFAULT, Strategy.CONTINOUS]


def should_run_during_method(strategy: Strategy) -> bool:
    return strategy in [Strategy.DURING_METHOD, Strategy.CONTINOUS]


def run_gate_hypothesis(experiment: Experiment, journal: Journal,
                        configuration: Configuration, secrets: Secrets,
                        event_registry: EventHandlerRegistry,
                        dry: bool = False) -> Dict[str, Any]:
    """
    Run the hypothesis before the method and bail the execution if it did
    not pass.
    """
    logger.debug("Running steady-state hypothesis before the method")
    event_registry.start_hypothesis_before(experiment)
    state = run_steady_state_hypothesis(
        experiment, configuration, secrets, dry=dry)
    journal["steady_states"]["before"] = state
    event_registry.hypothesis_before_completed(experiment, state, journal)
    if state is not None and not state["steady_state_met"]:
        journal["steady_states"]["before"] = state
        journal["status"] = "failed"

        p = state["probes"][-1]
        logger.fatal(
            "Steady state probe '{p}' is not in the given "
            "tolerance so failing this experiment".format(
                p=p["activity"]["name"]))
        return
    return state


def run_deviation_validation_hypothesis(experiment: Experiment,
                                        journal: Journal,
                                        configuration: Configuration,
                                        secrets: Secrets,
                                        event_registry: EventHandlerRegistry,
                                        dry: bool = False) \
                                            -> Dict[str, Any]:
    """
    Run the hypothesis after the method and report to the journal if the
    experiment has deviated.
    """
    logger.debug("Running steady-state hypothesis after the method")
    event_registry.start_hypothesis_after(experiment)
    state = run_steady_state_hypothesis(
        experiment, configuration, secrets, dry=dry)
    journal["steady_states"]["after"] = state
    event_registry.hypothesis_after_completed(experiment, state, journal)
    if state is not None and \
            not state["steady_state_met"]:
        journal["deviated"] = True
        journal["status"] = "failed"
        p = state["probes"][-1]
        logger.fatal(
            "Steady state probe '{p}' is not in the "
            "given tolerance so failing this "
            "experiment".format(
                p=p["activity"]["name"]))
    return state


def run_hypothesis_during_method(hypo_pool: ThreadPoolExecutor,
                                 continous_hypo_event: threading.Event,
                                 strategy: Strategy, schedule: Schedule,
                                 experiment: Experiment, journal: Journal,
                                 configuration: Configuration,
                                 secrets: Secrets,
                                 event_registry: EventHandlerRegistry,
                                 dry: bool = False) -> Future:
    """
    Run the hypothesis continously in a background thead and report the
    status in the journal when it raised an exception.
    """
    def completed(f: Future):
        exc = f.exception()
        event_registry.continous_hypothesis_completed(
            experiment, journal, exc)
        if exc is not None:
            if isinstance(exc, InterruptExecution):
                journal["status"] = "interrupted"
                logger.fatal(str(exc))
            elif isinstance(exc, Exception):
                journal["status"] = "aborted"
                logger.fatal(str(exc))
        logger.info("Continous steady state hypothesis terminated")

    f = hypo_pool.submit(
        run_hypothesis_continuously, continous_hypo_event,
        schedule, experiment, journal, configuration, secrets,
        event_registry, dry=dry)
    f.add_done_callback(completed)
    return f


def run_method(strategy: Strategy, activity_pool: ThreadPoolExecutor,
               experiment: Experiment, journal: Journal,
               configuration: Configuration, secrets: Secrets,
               event_registry: EventHandlerRegistry,
               dry: bool = False,
               actionless: bool = False) -> Optional[List[Run]]:
    logger.info("Playing your experiment's method now...")
    event_registry.start_method(experiment)
    try:
        state = apply_activities(
            experiment, configuration, secrets, activity_pool,
            journal, dry, actionless)
        event_registry.method_completed(experiment, state)
        return state
    except InterruptExecution:
        event_registry.method_completed(experiment)
        raise
    except Exception:
        journal["status"] = "aborted"
        event_registry.method_completed(experiment)
        logger.fatal(
            "Experiment ran into an un expected fatal error, "
            "aborting now.", exc_info=True)


def run_rollback(rollback_strategy: str, rollback_pool: ThreadPoolExecutor,
                 experiment: Experiment, journal: Journal,
                 configuration: Configuration, secrets: Secrets,
                 event_registry: EventHandlerRegistry,
                 dry: bool = False,
                 actionless: bool = False) -> None:
    has_deviated = journal["deviated"]
    journal_status = journal["status"]
    play_rollbacks = False
    if rollback_strategy == "always":
        logger.warning(
            "Rollbacks were explicitly requested to be played")
        play_rollbacks = True
    elif rollback_strategy == "never":
        logger.warning(
            "Rollbacks were explicitly requested to not be played")
        play_rollbacks = False
    elif rollback_strategy == "default" and \
            journal_status not in ["failed", "interrupted"]:
        play_rollbacks = True
    elif rollback_strategy == "deviated":
        if has_deviated:
            logger.warning(
                "Rollbacks will be played only because the experiment "
                "deviated")
            play_rollbacks = True
        else:
            logger.warning(
                "Rollbacks werre explicitely requested to be played "
                "only if the experiment deviated. Since this is not "
                "the case, we will not play them.")

    if play_rollbacks:
        event_registry.start_rollbacks(experiment)
        try:
            journal["rollbacks"] = apply_rollbacks(
                experiment, configuration, secrets,
                rollback_pool, dry, actionless)
        except InterruptExecution as i:
            journal["status"] = "interrupted"
            logger.fatal(str(i))
        except (KeyboardInterrupt, SystemExit):
            journal["status"] = "interrupted"
            logger.warning(
                "Received an exit signal."
                "Terminating now without running the "
                "remaining rollbacks.")
        finally:
            event_registry.rollbacks_completed(experiment, journal)


def initialize_run_journal(experiment: Experiment) -> Journal:
    return {
        "chaoslib-version": __version__,
        "platform": platform.platform(),
        "node": platform.node(),
        "experiment": experiment.copy(),
        "start": datetime.utcnow().isoformat(),
        "status": None,
        "deviated": False,
        "steady_states": {
            "before": None,
            "after": None,
            "during": []
        },
        "run": [],
        "rollbacks": []
    }


def get_background_pools(experiment: Experiment) -> ThreadPoolExecutor:
    """
    Create a pool for background activities. The pool is as big as the number
    of declared background activities. If none are declared, returned `None`.
    """
    method = experiment.get("method", [])
    rollbacks = experiment.get("rollbacks", [])

    activity_background_count = 0
    for activity in method:
        if activity and activity.get("background"):
            activity_background_count = activity_background_count + 1

    activity_pool = None
    if activity_background_count:
        logger.debug(
            "{c} activities will be run in the background".format(
                c=activity_background_count))
        activity_pool = ThreadPoolExecutor(activity_background_count)

    rollback_background_pool = 0
    for activity in rollbacks:
        if activity and activity.get("background"):
            rollback_background_pool = rollback_background_pool + 1

    rollback_pool = None
    if rollback_background_pool:
        logger.debug(
            "{c} rollbacks will be run in the background".format(
                c=rollback_background_pool))
        rollback_pool = ThreadPoolExecutor(rollback_background_pool)

    return activity_pool, rollback_pool


def get_hypothesis_pool() -> ThreadPoolExecutor:
    """
    Create a pool for running the steady-state hypothesis continuously in the
    background of the method. The pool is not bounded because we don't know
    how long it will run for.
    """
    return ThreadPoolExecutor(max_workers=1)


def run_hypothesis_continuously(event: threading.Event, schedule: Schedule,
                                experiment: Experiment, journal: Journal,
                                configuration: Configuration,
                                secrets: Secrets,
                                event_registry: EventHandlerRegistry,
                                dry: bool = False):
    frequency = schedule.continous_hypothesis_frequency
    fail_fast_ratio = schedule.fail_fast_ratio

    event_registry.start_continous_hypothesis(frequency)
    logger.info(
        "Executing the steady-state hypothesis continously "
        "every {} seconds".format(frequency))

    failed_iteration = 0
    failed_ratio = 0
    iteration = 1
    while not event.is_set():
        # already marked as terminated, let's exit now
        if journal["status"] in ["failed", "interrupted", "aborted"]:
            break

        state = run_steady_state_hypothesis(
            experiment, configuration, secrets, dry=dry)
        journal["steady_states"]["during"].append(state)
        event_registry.continous_hypothesis_iteration(iteration, state)

        if state is not None and not state["steady_state_met"]:
            failed_iteration += 1
            failed_ratio = (failed_iteration * 100) / iteration
            p = state["probes"][-1]
            logger.warning(
                "Continous steady state probe '{p}' is not in the given "
                "tolerance".format(p=p["activity"]["name"]))

            if schedule.fail_fast:
                if failed_ratio >= fail_fast_ratio:
                    m = "Terminating immediatly the experiment"
                    if failed_ratio != 0.0:
                        m = "{} after {:.1f}% hypothesis deviated".format(
                            m, failed_ratio
                        )
                    logger.info(m)
                    journal["status"] = "failed"
                    break
        iteration += 1

        # we do not adjust the frequency based on the time taken by probes
        # above. We really want frequency seconds between two iteration
        # not frequency as a total time of a single iteration
        event.wait(timeout=frequency)


def apply_activities(experiment: Experiment, configuration: Configuration,
                     secrets: Secrets, pool: ThreadPoolExecutor,
                     journal: Journal,
                     dry: bool = False, actionless: bool = False) -> List[Run]:
    with controls(level="method", experiment=experiment, context=experiment,
                  configuration=configuration, secrets=secrets) as control:
        result = []
        runs = []
        method = experiment.get("method", [])
        wait_for_background_activities = True

        try:
            for run in run_activities(
                    experiment, configuration, secrets, pool, dry, actionless):
                runs.append(run)
                if journal["status"] in ["aborted", "failed", "interrupted"]:
                    break
        except SystemExit as x:
            # when we got a signal for an ungraceful exit, we can decide
            # not to wait for background activities. Their statuses will
            # remain failed.
            wait_for_background_activities = x.code != 30  # see exit.py
            raise
        finally:
            background_activity_timeout = None

            if wait_for_background_activities and pool:
                logger.debug("Waiting for background activities to complete")
                pool.shutdown(wait=True)
            elif pool:
                harshly_terminate_pending_background_activities(pool)
                logger.debug(
                    "Do not wait for the background activities to finish "
                    "as per signal")
                background_activity_timeout = 0.2
                pool.shutdown(wait=False)

            for index, run in enumerate(runs):
                if not run:
                    continue

                if isinstance(run, dict):
                    result.append(run)
                else:
                    try:
                        # background activities
                        result.append(
                            run.result(timeout=background_activity_timeout))
                    except TimeoutError:
                        # we want an entry for the background activity in our
                        # results anyway, we won't have anything meaningful
                        # to say about it
                        result.append({
                            "activity": method[index],
                            "status": "failed",
                            "output": None,
                            "duration": None,
                            "start": None,
                            "end": None,
                            "exception": None
                        })

            # now let's ensure the journal has all activities in their correct
            # order (background ones included)
            journal["run"] = result

            control.with_state(result)

    return result


def apply_rollbacks(experiment: Experiment, configuration: Configuration,
                    secrets: Secrets, pool: ThreadPoolExecutor,
                    dry: bool = False,
                    actionless: bool = False) -> List[Run]:
    logger.info("Let's rollback...")
    with controls(level="rollback", experiment=experiment, context=experiment,
                  configuration=configuration, secrets=secrets) as control:
        rollbacks = list(
            run_rollbacks(experiment, configuration, secrets, pool, dry,
                          actionless))

        if pool:
            logger.debug("Waiting for background rollbacks to complete...")
            pool.shutdown(wait=True)

        result = []
        for rollback in rollbacks:
            if not rollback:
                continue
            if isinstance(rollback, dict):
                result.append(rollback)
            else:
                result.append(rollback.result())

        control.with_state(result)

    return result


def has_steady_state_hypothesis_with_probes(experiment: Experiment) -> bool:
    steady_state_hypothesis = experiment.get("steady-state-hypothesis")
    if steady_state_hypothesis:
        probes = steady_state_hypothesis.get("probes")
        if probes:
            return len(probes) > 0
    return False


def harshly_terminate_pending_background_activities(
        pool: ThreadPoolExecutor) -> None:
    """
    Ugly hack to try to force background activities to terminate now.

    This cano only have an impact over functions that are still in the Python
    land. Any code outside of the Python VM (say calling a C function, even
    time.sleep()) will not be impacted and therefore will continue hanging
    until it does complete of its own accord.

    This could have really bizarre side effects so it's only applied when
    a SIGUSR2 signal was received.
    """
    if not HAS_CTYPES:
        logger.debug(
            "Your Python implementation does not provide the `ctypes` "
            "module and we cannot terminate very harshly running background "
            "activities.")
        return

    logger.debug(
        "Harshly trying to interrupt remaining background activities still "
        "running")

    # oh and of course we use private properties... might as well when trying
    # to be ugly
    for thread in pool._threads:
        tid = ctypes.c_long(thread.ident)
        try:
            gil = ctypes.pythonapi.PyGILState_Ensure()
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                tid, ctypes.py_object(ExperimentExitedException))
        finally:
            ctypes.pythonapi.PyGILState_Release(gil)
