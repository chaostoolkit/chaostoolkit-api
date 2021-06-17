from copy import deepcopy
import os
EmptyAction = {}


DoNothingAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "do_nothing"
    }
}


EchoAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "echo_message",
        "arguments": {
            "message": "kaboom"
        }
    }
}


FailAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "force_failed_activity"
    }
}


InterruptAction = {
    "name": "a name",
    "type": "action",
    "provider": {
        "type": "python",
        "module": "fixtures.fakeext",
        "func": "force_interrupting_experiment"
    }
}

PythonModuleActionWithLongPause = {
    "type": "action",
    "name": "action-with-long-pause",
    "pauses": {
        "before": 30,
        "after": 5
    },
    "provider": {
        "type": "python",
        "module": "os.path",
        "func": "exists",
        "arguments": {
            "path": os.path.abspath(__file__),
        },
        "timeout": 40
    }
}

PythonModuleActionWithLongAction = deepcopy(PythonModuleActionWithLongPause)
PythonModuleActionWithLongAction["pauses"]["after"] = 30
PythonModuleActionWithLongAction["pauses"]["before"] = 35
