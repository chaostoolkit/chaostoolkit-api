# -*- coding: utf-8 -*-
from copy import deepcopy

from fixtures.probes import BackgroundPythonModuleProbe, MissingFuncArgProbe, \
    PythonModuleProbe, PythonModuleProbeWithBoolTolerance, \
    PythonModuleProbeWithExternalTolerance, PythonModuleProbeWithLongPause, \
    BackgroundPythonModuleProbeWithLongPause, \
    PythonModuleProbeWithHTTPStatusTolerance, DeprecatedProcArgumentsProbe, \
    PythonModuleProbeWithHTTPBodyTolerance, \
    PythonModuleProbeWithProcessStatusTolerance, \
    PythonModuleProbeWithProcessFailedStatusTolerance, \
    PythonModuleProbeWithProcesStdoutTolerance

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



ExperimentWithControls = {
    "title": "do cats live in the Internet?",
    "description": "an experiment of importance",
    "controls": [
        {
            "name": "dummy",
            "provider": {
                "type": "python",
                "module": "fixtures.controls.dummy"
            }
        }
    ],
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
