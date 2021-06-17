# -*- coding: utf-8 -*-
from copy import deepcopy
import os

from fixtures.actions import DoNothingAction, EchoAction, FailAction, \
    InterruptAction,\
    PythonModuleActionWithLongAction
from fixtures.probes import BackgroundPythonModuleProbe, MissingFuncArgProbe, \
    PythonModuleProbe, PythonModuleProbeWithBoolTolerance, \
    PythonModuleProbeWithExternalTolerance, PythonModuleProbeWithLongPause, \
    BackgroundPythonModuleProbeWithLongPause, BackgroundPythonModuleProbeWithLongPauseBefore,\
    PythonModuleProbeWithHTTPStatusTolerance, DeprecatedProcArgumentsProbe, \
    PythonModuleProbeWithHTTPBodyTolerance, \
    PythonModuleProbeWithProcessStatusTolerance, \
    PythonModuleProbeWithProcessFailedStatusTolerance, \
    PythonModuleProbeWithProcesStdoutTolerance, \
    PythonModuleProbeWithHTTPStatusToleranceDeviation, FailProbe, \
    GenerateSecretTokenProbe, ReadSecretTokenProbe, \
    ReadSecretTokenFromSecretsProbe

Secrets = {}

EmptyExperiment = {}

MissingTitleExperiment = {
    "description": "blah"
}

MissingDescriptionExperiment = {
    "title": "kaboom"
}

MissingHypothesisExperiment = {
    "title": "kaboom",
    "description": "blah",
    "method": [PythonModuleProbeWithBoolTolerance]
}

MissingHypothesisTitleExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {},
    "method": []
}

MissingMethodExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {
        "title": "hello"
    }
}

NoStepsMethodExperiment = {
    "title": "kaboom",
    "description": "blah",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": []
}

ExperimentWithInvalidHypoProbe = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            MissingFuncArgProbe
        ]
    },
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ],
    "rollbacks": [
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}

ExperimentWithInterpolatedTitle = {
    "configuration": {
        "project_name": {
            "type": "env",
            "key": "PROJECT_NAME",
            "default": "Cats in space"
        }
    },
    "dry_run": True,
    "title": "${project_name}: do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
        ]
    },
    "method": [
        PythonModuleProbe,
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}

ExperimentWithLongPause = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        PythonModuleProbeWithLongPause,
        BackgroundPythonModuleProbeWithLongPause
    ],
    "rollbacks": [
        BackgroundPythonModuleProbe
    ]
}

ExperimentWithLongPauseAction = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        PythonModuleProbeWithLongPause,
        PythonModuleActionWithLongAction,
    ],
    "rollbacks": [
        PythonModuleActionWithLongAction
    ]
}

ExperimentWithRollbackLongPause = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        PythonModuleProbe
    ],
    "rollbacks": [
        PythonModuleProbeWithLongPause
    ]
}

ExperimentWithLongPauseBefore = deepcopy(ExperimentWithLongPause)
ExperimentWithLongPauseBefore["method"][1] = BackgroundPythonModuleProbeWithLongPauseBefore

RefProbeExperiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
        ]
    },
    "method": [
        PythonModuleProbe,
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}

MissingRefProbeExperiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
        ]
    },
    "method": [
        PythonModuleProbe,
        {
            "ref": "pizza"
        }
    ]
}

HTTPToleranceExperiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithHTTPStatusTolerance
        ]
    },
    "method": [],
    "rollbacks": []
}


DeprecatedProcArgumentsProbeTwin = DeprecatedProcArgumentsProbe.copy()
DeprecatedProcArgumentsProbeTwin["name"] = "another-proc-probe"

ExperimentWithDeprecatedProcArgsProbe = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "method": [
        DeprecatedProcArgumentsProbe,
        DeprecatedProcArgumentsProbeTwin
    ]
}

ExperimentWithDeprecatedVaultPayload = {
    "title": "vault is missing a path",
    "description": "an experiment of importance",
    "secrets": {
        "k8s": {
            "some-key": {
                "type": "vault",
                "key": "foo"
            }
        }
    },
    "method": []
}


Experiment = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
            PythonModuleProbeWithHTTPStatusTolerance,
            PythonModuleProbeWithExternalTolerance
        ]
    },
    "method": [
        PythonModuleProbe, BackgroundPythonModuleProbe
    ],
    "rollbacks": [
        {
            "ref": PythonModuleProbe["name"]
        }
    ]
}


ExperimentWithConfigurationCallingMissingEnvKey = Experiment.copy()
ExperimentWithConfigurationCallingMissingEnvKey["configuration"] = {
    "mykey": {
        "type": "env",
        "key": "DOES_NOT_EXIST"
    }
}


ExperimentWithVariousTolerances = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            PythonModuleProbeWithBoolTolerance,
            PythonModuleProbeWithExternalTolerance,
            PythonModuleProbeWithHTTPStatusTolerance,
            PythonModuleProbeWithHTTPBodyTolerance,
            PythonModuleProbeWithProcessStatusTolerance,
            PythonModuleProbeWithProcessFailedStatusTolerance,
            PythonModuleProbeWithProcesStdoutTolerance
        ]
    },
    "method": [
        PythonModuleProbe
    ],
    "rollbacks": []
}


ExperimentNoControls = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            deepcopy(PythonModuleProbeWithBoolTolerance)
        ]
    },
    "method": [
        deepcopy(PythonModuleProbe)
    ],
    "rollbacks": [
        deepcopy(PythonModuleProbeWithBoolTolerance)
    ]
}


ExperimentNoControlsWithDeviation = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            deepcopy(PythonModuleProbeWithHTTPStatusToleranceDeviation)
        ]
    },
    "method": [
        deepcopy(PythonModuleProbe)
    ],
    "rollbacks": [
        deepcopy(PythonModuleProbeWithBoolTolerance)
    ]
}


ExperimentWithControls = deepcopy(ExperimentNoControls)
ExperimentWithControls["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy"
        }
    }
]

ExperimentWithDecoratedControls = deepcopy(ExperimentNoControls)
ExperimentWithDecoratedControls["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_with_decorated_control"
        }
    }
]

ExperimentWithControlsRequiringSecrets = deepcopy(ExperimentWithControls)
ExperimentWithControlsRequiringSecrets["secrets"] = {
    "mystuff": {
        "somesecret": "somevalue"
    }
}
ExperimentWithControlsRequiringSecrets["controls"][0]["provider"]["module"] = "fixtures.controls.dummy_with_secrets"
ExperimentWithControlsRequiringSecrets["controls"][0]["provider"]["secrets"] = ["mystuff"]

ExperimentWithControlsThatUpdatedConfiguration = deepcopy(ExperimentNoControls)
ExperimentWithControlsThatUpdatedConfiguration["configuration"] = {
    "my_token": "UNSET"
}
ExperimentWithControlsThatUpdatedConfiguration["method"] = [
    deepcopy(GenerateSecretTokenProbe),
    deepcopy(ReadSecretTokenProbe)
]
ExperimentWithControlsThatUpdatedConfiguration["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_changed_configuration"
        }
    }
]

ExperimentWithControlsThatUpdatedSecrets = deepcopy(ExperimentNoControls)
ExperimentWithControlsThatUpdatedSecrets["secrets"] = {
    "mytokens": {
        "my_token": "UNSET"
    }
}
ExperimentWithControlsThatUpdatedSecrets["method"] = [
    deepcopy(GenerateSecretTokenProbe),
    deepcopy(ReadSecretTokenFromSecretsProbe)
]
ExperimentWithControlsThatUpdatedSecrets["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_changed_secrets"
        }
    }
]

ExperimentWithArgumentsControls = deepcopy(ExperimentNoControls)
ExperimentWithArgumentsControls["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_args_in_control_init",
            "arguments": {
                "joke": "onyou"
            }
        }
    }
]


ExperimentWithUnexpectedArgumentsControls = deepcopy(ExperimentNoControls)
ExperimentWithUnexpectedArgumentsControls["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy",
            "arguments": {
                "joke": "onyou"
            }
        }
    }
]

ExperimentUsingConfigToConfigureControls = deepcopy(ExperimentNoControls)
ExperimentUsingConfigToConfigureControls["configuration"] = {
    "dummy-key": "blah blah"
}


ExperimentWithControlsAtVariousLevels = deepcopy(ExperimentWithControls)
ExperimentWithControlsAtVariousLevels["method"][0]["controls"] = [
        {
            "name": "dummy-two",
            "provider": {
                "type": "python",
                "module": "fixtures.controls.dummy"
            }
        }
    ]


ExperimentWithControlNotAtTopLevel = deepcopy(ExperimentWithControls)
ExperimentWithControlNotAtTopLevel.pop("controls")
ExperimentWithControlNotAtTopLevel["method"][0]["controls"] = [
        {
            "name": "dummy",
            "provider": {
                "type": "python",
                "module": "fixtures.controls.dummy"
            }
        }
    ]


ExperimentWithControlAccessingExperiment = deepcopy(ExperimentWithControls)
ExperimentWithControlAccessingExperiment["controls"][0]["provider"]["module"] = "fixtures.controls.dummy_with_experiment"

ExperimentCanBeInterruptedByControl = deepcopy(ExperimentWithControls)
ExperimentCanBeInterruptedByControl["controls"] = [
    {
        "name": "aborter",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.interrupter"
        }
    }
]


ExperimentWithoutControls = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
        deepcopy(PythonModuleProbeWithBoolTolerance)
        ]
    },
    "method": [
        deepcopy(PythonModuleProbe)
    ],
    "rollbacks": [
        deepcopy(PythonModuleProbeWithBoolTolerance)
    ]
}

# we should be conservative about reading experiments
UnsafeYamlExperiment = """
!!python/object/apply:os.system\nargs: ['Hello shell!']
"""

YamlExperiment = """
---
title: do cats live in the Internet?
description: an experiment of importance
method:
- type: probe
  name: path-must-exists
  pauses:
    before: 0
    after: 0.1
  provider:
    type: python
    module: os.path
    func: exists
    arguments:
      path: {}
    timeout: 30
""".format(os.path.abspath(__file__))


SimpleExperiment = {
    "version": "1.0.0",
    "title": "Hello world!",
    "description": "Say hello world.",
    "steady-state-hypothesis": {
        "title": "World needs politeness",
        "probes": [
            {
                "type": "probe",
                "name": "has-world",
                "tolerance": 0,
                "provider": {
                "type": "process",
                "path": "echo",
                    "arguments": "hello"
                }
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "say-hello",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "world"
            },
            "pauses": {
                "after": 1
            }
        }
    ]
}


SimpleExperimentWithInterruption = deepcopy(SimpleExperiment)
SimpleExperimentWithInterruption["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_with_interrupted_activity",
            "arguments": {
                "target_activity_name": "say-hello"
            }
        }
    }
]


SimpleExperimentWithExit = deepcopy(SimpleExperiment)
SimpleExperimentWithExit["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.controls.dummy_with_exited_activity",
            "arguments": {
                "target_activity_name": "say-hello"
            }
        }
    }
]


SimpleExperimentWithException = deepcopy(SimpleExperiment)
SimpleExperimentWithException["method"].append(
    {
        "type": "action",
        "name": "boom",
        "provider": {
            "type": "python",
            "module": "fixtures.badstuff",
            "func": "raise_exception"
        }
    }
)


SimpleExperimentWithSSHFailingAtSomePoint = deepcopy(SimpleExperiment)
SimpleExperimentWithSSHFailingAtSomePoint["method"][0]["pauses"]["after"] = 2
SimpleExperimentWithSSHFailingAtSomePoint["method"].append(
    {
        "type": "action",
        "name": "say-hello-in-french",
        "provider": {
            "type": "process",
            "path": "echo",
            "arguments": "bonjour"
        },
        "pauses": {
            "before": 1
        }
    }
)
SimpleExperimentWithSSHFailingAtSomePoint["steady-state-hypothesis"]["probes"].append(
    {
        "type": "probe",
        "name": "fail-at-somepoint",
        "tolerance":  {
            "type": "probe",
            "name": "check-lower-than",
            "provider": {
                "type": "python",
                "module": "fixtures.badstuff",
                "func": "check_under_treshold",
                "arguments": {
                    "target": 2
                }
            }
        },
        "provider": {
            "type": "python",
            "module": "fixtures.badstuff",
            "func": "count_generator"
        }
    }
)
SimpleExperimentWithSSHFailingAtSomePoint["rollbacks"] = [
    {
        "type": "action",
        "name": "cleanup",
        "provider": {
            "type": "python",
            "module": "fixtures.badstuff",
            "func": "cleanup_counter"
        }
    }
]

SimpleExperimentWithSSHFailingAtSomePointWithBackgroundActivity = deepcopy(
    SimpleExperimentWithSSHFailingAtSomePoint
)
SimpleExperimentWithSSHFailingAtSomePointWithBackgroundActivity["method"][0]["background"] = True
SimpleExperimentWithSSHFailingAtSomePointWithBackgroundActivity["method"][0]["pauses"]["after"] = 2

ExperimentWithRegularRollback = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        EchoAction
    ],
    "rollbacks": [
        EchoAction
    ]
}


ExperimentWithFailedActionInMethodAndARollback = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        FailAction
    ],
    "rollbacks": [
        EchoAction
    ]
}


ExperimentWithFailedActionInSSHAndARollback = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello",
        "probes": [
            FailProbe
        ]
    },
    "method": [
        DoNothingAction
    ],
    "rollbacks": [
        EchoAction
    ]
}


ExperimentWithInterruptedExperimentAndARollback = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "steady-state-hypothesis": {
        "title": "hello"
    },
    "method": [
        deepcopy(EchoAction)
    ],
    "rollbacks": [
        EchoAction
    ]
}
ExperimentWithInterruptedExperimentAndARollback["method"][0]["controls"] = [
    {
        "name": "dummy",
        "provider": {
            "type": "python",
            "module": "fixtures.interruptexperiment"
        }
    }
]


ExperimentGracefulExitLongHTTPCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "do-whatever-in-the-background",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long"
            }
        },
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_gracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "http",
                "url": "http://localhost:8700/"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


ExperimentGracefulExitLongProcessCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_gracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "process",
                "path": "cat",
                "arguments": "-"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


ExperimentGracefulExitLongPythonCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_gracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


ExperimentUngracefulExitLongHTTPCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "do-whatever-in-the-background",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long"
            }
        },
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_ungracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "http",
                "url": "http://localhost:8700"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


ExperimentUngracefulExitLongProcessCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_ungracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "process",
                "path": "cat",
                "arguments": "-"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


ExperimentUngracefulExitLongPythonCall = {
    "version": "1.0.0",
    "title": "Say hello and kaboom",
    "description": "n/a",
    "method": [
        {
            "type": "probe",
            "name": "interrupt-next-action",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.interrupter",
                "func": "interrupt_ungracefully_in"
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long"
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "echo-rollback-is-done",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "done!!"
            }
        }
    ]
}


SimpleExperimentWithFailingHypothesis = {
    "version": "1.0.0",
    "title": "Hello world!",
    "description": "Say hello world.",
    "steady-state-hypothesis": {
        "title": "World needs politeness",
        "probes": [
            {
                "type": "probe",
                "name": "has-world",
                "tolerance": 1,
                "provider": {
                "type": "process",
                "path": "echo",
                    "arguments": "hello"
                }
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "say-hello",
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "world"
            },
            "pauses": {
                "after": 1
            }
        }
    ]
}


SimpleExperimentWithBackgroundActivity = {
    "version": "1.0.0",
    "title": "Hello world!",
    "description": "Say hello world.",
    "method": [
        {
            "type": "action",
            "name": "pretend-we-do-stuff",
            "background": True,
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long",
                "arguments": {
                    "howlong": 3
                }
            }
        },
        {
            "type": "action",
            "name": "pretend-we-do-stuff-again",
            "provider": {
                "type": "python",
                "module": "fixtures.longpythonfunc",
                "func": "be_long",
                "arguments": {
                    "howlong": 4
                }
            }
        }
    ]
}

ExperimentWithBypassedActivity = {
    "version": "1.0.0",
    "title": "do stuff",
    "description": "n/a",
    "method": [
        {
            "type": "action",
            "name": "say-hello",
            "dry": True,
            "provider": {
                "type": "process",
                "path": "echo",
                "arguments": "hello"
            }
        }
    ]
}
