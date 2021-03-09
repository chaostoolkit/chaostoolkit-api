# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.19.0...HEAD

## [1.19.0][] - 2021-02-16

[1.19.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.18.3...1.19.0

### Changed

- Library now requires Python 3.6 [#208][ctk208]

[ctk208]: https://github.com/chaostoolkit/chaostoolkit/issues/208

## [1.18.3][] - 2021-02-16

[1.18.3]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.18.2...1.18.3

### Changed

- Fix typo in `setup.cfg` from `install_require` to `install_requires`

## [1.18.2][] - 2021-02-16

[1.18.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.18.1...1.18.2

### Changed

- Fix release workflow by updating to latest setuptools

## [1.18.1][] - 2021-02-16

[1.18.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.18.0...1.18.1

### Changed

- Fix release package

## [1.18.0][] - 2021-02-16

[1.18.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.17.0...1.18.0

### Changed

- Moved from setup.py to declarative setup.cfg [#204][204]
- Moved to pylama from pycodestyle [#205][205]

[204]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/204
[205]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/205

## [1.17.0][] - 2021-02-15

[1.17.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.16.0...1.17.0

### Added

- Activities can be requested not to be executed on a per activity basis, not
  just as all or none. This can be used by a control to dynamically make
  a decision on what to run.
- Test that demonstrate how to wrap controls into decorators [#197][197]

[197]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/197

### Changed

- Moved from TravisCI to GitHub Workflows [#201][201]

[201]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/201

## [1.16.0][] - 2020-12-02

[1.16.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.15.1...1.16.0

### Changed

- Allow substitution to keep its original type when done in isolation.
  [#180][180] [#195][195]. So let's assume we have the following configuration:

  ```json
  "configuration": {
      "value": 8
  }
  ```

  We can now use it as an argument of an action:

  ```json
  "provider": {
      "arguments": {
          "quantity": "${value}"
      }
  }
  ```

  Now, the `quantity` argument will indeed be an integer, when it was converted
  to string until now. This works with any support Python objects, whether they
  are scalars or nested.

  If, you have something like this however


  ```json
  "provider": {
      "arguments": {
          "quantity": "I want ${value} apples"
      }
  }
  ```

  This will always remain a string.


[180]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/180
[195]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/195

## [1.15.1][] - 2020-11-02

[1.15.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.15.0...1.15.1

### Changed

- Fixed a regression where the extra vars were not passed onto configuration
  and secrets for overriding substitution [#192][192]

[192]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/192

### Added

- New field `expect_one_of` in `jsonpath` tolerance. Sometimes the json payload
  values will be dynamic, e.g. field `status` in response payload may provide
  any values(either `ok` or `error` or `info`). Using `expect` field, we can
  mention only one value as expected value but sometimes steady state can be
  met with one or more values. e.g. you want to define two values either `ok` or
  `info` as expected value. In these cases, you can use both `expect` and
  `expect_one_of` to define both expected values.[#191][191]

[191]: https://github.com/chaostoolkit/chaostoolkit-lib/pull/191


## [1.15.0][] - 2020-09-11

[1.15.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.14.1...1.15.0

### Added

- Raise the `chaoslib.exceptions.InterruptExecution` on `SIGTERM`
- New exception `chaoslib.exceptions.ExperimentExitedException` that can only
  be injected into blocking background activities when we received the SIGUSR2
  signal
- We now inject `chaoslib.exceptions.ExperimentExitedException` into blocking
  background activities when we received the SIGUSR2 signal. This is relying
  on https://docs.python.org/3/c-api/init.html#c.PyThreadState_SetAsyncExc
  There is much we can to interrupt blocking calls and the limit is now reached
  because we have no control over any call that is out of the Python VM (just
  calling `time.sleep()` will get you in that situation). This is a constraint
  we have to live in and this extension authors must keep this in mind when
  they create their blocking calls. [#185][185]

## [1.14.1][] - 2020-09-10

[1.14.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.14.0...1.14.1

### Added

- SIGTERM signal is now listened for. This triggers the interruption mechanism
  of the experiment.

## [1.14.0][] - 2020-09-09

[1.14.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.13.1...1.14.0

### Added

- Add two functions to programmatically exit the experiment as soon as feasible
  by the Python VM [#185][185]:
  * `chaoslib.exit.exit_gracefully`: termintes but abides to the rollback strategy
  * `chaoslib.exit.exit_ungracefully`: termintes but bypasses rollbacks entirely
    and does not wait for background actions/probes still running
  This should mostly be useful to have a harsh way to interrupt an execution
  and is therefore an advanced concept with undesirable side effects (though
  Chaos Toolkit tries to do as right as it can).

  CAVEAT: Only works on Unix/Linux systems implementing SIGUSR1/SIGUSR2 signals

[185]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/185


### Changed

- Fix [chaostoolkit#192][chaostoolkit192] to make sure a failing hypothesis
  prevents the method to be executed.

[chaostoolkit192]: https://github.com/chaostoolkit/chaostoolkit/issues/192

## [1.13.1][] - 2020-09-07

[1.13.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.13.0...1.13.1

### Changed

- Ensure the method is always executed, even when no steady-state was provided
  in the experiment.

## [1.13.0][] - 2020-09-07

[1.13.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.12.0...1.13.0

### Added

- Steady-state hypothesos runtime strategies can be now set to determine if the
  the hypothesis is executed before/after the method as usual (default behavior)
  or continously throughout the method too. Yo ucan also make it applied
  before or after only, or even only during the method. [#191][191]

[191]: https://github.com/chaostoolkit/chaostoolkit/pull/191

### Changed

- Always pass all secrets to control hookpoints [#187][187]
- Massive refactor of the `run_experiment` function so that it raises now events
  of where it is during the execution so that external plugins to the Chaos
  Toolkit can react and impact the run. This goes beyond mere controls and
  is advanced usage. Still, this is a public interface. [#178][178]
  In theory, this is an internal change only and the `run_experiment` function
  has not changed its API. However, this may have deep impact if you already
  depended on its internals.

[187]: https://github.com/chaostoolkit/chaostoolkit/issues/187
[178]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/178

## [1.12.0][] - 2020-08-17

[1.12.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.11.1...1.12.0

### Added

- Added ways to override configuration and secrets from var files or passed to
  the chaostoolkit cli [chaostoolkit#175][].

### Changed

- Always ensure the [status][statuses] in the journal is one of
  the specified value, with a default to `"completed"`.

[statuses]: https://docs.chaostoolkit.org/reference/api/journal/#required-properties

[chaostoolkit#175]: https://github.com/chaostoolkit/chaostoolkit/issues/175

## [1.11.1][] - 2020-07-29

[1.11.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.11.0...1.11.1

### Changed

- Controls can now update/change configuration and secrets on the fly as per
  the specification [#181][181]

[181]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/181

## [1.11.0][] - 2020-07-06

[1.11.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.10.0...1.11.0

### Added

- Added runtime strategies for rollback as per [chaostoolkit#176][].
  Until now, they were never played
  an activity would fail during the hypothesis or if the execution
  was interrupted from a control. With the strategies, you can now decide
  that they are always applied, never or only when the experiment deviated.
  This is a flag passed to the settings as follows:

  ```
  runtime:
    rollbacks:
      strategy: "always|never|default|deviated"
  ```

  The `"default"` strategy remains backward compatible.

  [chaostoolkit#176]: https://github.com/chaostoolkit/chaostoolkit/issues/176

## [1.10.0][] - 2020-06-19

[1.10.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.9.0...1.10.0

### Added

- Added function to lookup a value in the settings from a dotted path
  key [chaostoolkit#65][65]

[65]: https://github.com/chaostoolkit/chaostoolkit/issues/65

## [1.9.0][] - 2020-04-29

[1.9.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.8.1...1.9.0

### Added

- Only apply rollbacks if experiment has progressed past the initial steady state hypothesis [#168](168)
- Allow to not verify certificates when connecting to a HTTPS endpoint using [#163](163)
  self-signed certificate.

[168]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/168
[163]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/163

### Added

- Refactored run of the experiment so that we can have multiple run strategies
  such as not running the steady-state hypothesis before or after the method
  but also one strategy so that the steady-state is continously applied
  during the method, with the option to bail the experiment as soon as it
  deviates. [#149][149]

### Changed

- Potentially breaking. The following functions have moved from
  `chaoslib.experiment` to `chaoslib.run`: `initialize_run_journal`,
  `apply_activities`, `apply_rollbacks`.

[149]: https://github.com/chaostoolkit/chaostoolkit/issues/149

### Changed

- Fix error on empty string variables call [#165][165]

[165]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/165


## [1.8.1][] - 2020-02-20

[1.8.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.8.0...1.8.1

### Added

- Build and test on Python 3.8

### Changed

- Fix importlib_metadata call [#162][162]

[162]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/162

## [1.8.0][] - 2020-02-20

[1.8.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.7.1...1.8.0

### Added

- Optional default value for environment variable in configuration
- Warn the user for an action process returning a non-zero exit code
- Support for process path relative to homedir ~
- Indicate path in validation when path is not found nor executable [#159][159]

### Changed

- Changed the method's one-step minimum requirement.
  An experiment with an empty method (without any activities) is now valid.

[159]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/159

## [1.7.1][] - 2019-09-27

[1.7.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.7.0...1.7.1

### Added

- Catch `InterruptExecution` during rollbacks so that the experiment terminates
  gracefully [#132][132].  The remaining rollbacks are not applied.
- Catch `SIGINT` and `SystemExit` during rollbacks so that the experiment
  terminates gracefully [#133][133]. The remaining rollbacks are not applied.

[132]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/132
[133]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/133

## [1.7.0][] - 2019-09-21

[1.7.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.6.0...1.7.0

### Changed

- Fix to ensure a dry run ignores pauses
- Allow substitution from configuration and secrets into regex and jsonpath
  tolerances

## [1.6.0][] - 2019-09-03

[1.6.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.5.0...1.6.0

### Added

- Two new control hook points before and after the experiment loading. These
  hooks allow a control to perform certain operations before the experiment
  is actually applied.
- Experiments can be loaded from HTTP server which returns them using a
  `text/plain`  content-type [#130][130]. This allows notably to run directly
  experiments hosted on GitHub.

[130]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/130

### Changed

- Add the `max_retries` parameter to the HTTP provider
- Changed nested tolerance Python probes to return `True` to the experiment in
  case the nested probe returns an object or `True`, and to return `False` in
  case of `None` or `False`. Before, `True` was returned every time except in case
  of an `ActivityFailed` exception. [#128][128].
- Global Python controls are now imported from a specific function called
  `load_global_controls(settings: Settings)`. The reason from loading them
  separately is so that we can have them declared, and registered, as soon
  as we can. Before, they were loaded when the experiments started to be
  executed. Now, we can also run controls when we read the experiment itself,
  which wasn't possible before.
- Read package version by readsing `__version__` from the `chaoslib/__init__.py`
  file directly without importing it, to avoid dependency issues of uninstalled
  third-party packages.

## [1.5.0][] - 2019-07-01

[1.5.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.4.0...1.5.0

### Changed

- Fix `expect` validation when the value is a scalar rather than a sequence.
- Controls inheritance was getting too greedy because we were extending the
  same list over and over again.
- Prevent control initializations' failure to bubble up
- Pass arguments to control initialization function when declared
- Interrupt nicely the experiment from control at the activity level

## [1.4.0][] - 2019-05-16

[1.4.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.3.1...1.4.0

### Changed

- [POTENTIALLY BREAKING] Changed the JSONPath implementation from `jsonpath-ng`
  to `jsonpath2` as the former does not fully, or correctly, implement the
  JSON Path specification. The latter is based on the ANTLR grammar and
  implements filters appropriately. The breaking aspect is due to the fact that
  your path may not work anylonger as they may be rejected by the new
  implementation which is more correct. [#119][119].

  Please install `jsonpath2`:

  ```
  $ pip install jsonpath2
  ```

[119]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/119

## [1.3.1][] - 2019-05-10

[1.3.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.3.0...1.3.1

### Changed

- Fix to pass control's state when probe fails during hypothesis [#118][118]

[118]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/118


## [1.3.0][] - 2019-05-04

[1.3.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.2.0...1.3.0

### Changed

- Fix to ensure a control's `configuration` parameter is populated when it the
  control is being `configured` [#114][114]
- Load and apply global controls, those declared in the settings, from the
  `run_experiment` function rather than out of band [#116][116]

  This means that global controls will not be applied before the experiment
  is validated but only when it's executed.

  It also means the global controls will be provided with the experiment, its
  configuration and secrets in case global controls must access these.

[114]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/114
[116]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/116


## [1.2.0][] - 2019-04-17

[1.2.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.1.2...1.2.0

### Changed

- Create settings directory when it doesn't already exist [#97][97]
- Pass configuration to tolerance checks so that probe tolerance can access it
  [#98][98]
- Fix using a probe as a tolerance validator [#98][98]
- Make settings globally available during the run [#99][99]
- Load controls from settings too now [#99][99]
- Do not build on MacOSX platform [#110][110]
- Run stable Python 3.7 build

[97]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/97
[98]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/98
[99]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/99
[110]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/110

## [1.1.2][] - 2019-03-22

[1.1.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.1.1...1.1.2

### Changed

- Use a YAML safe loader for settings [#92][92]

[92]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/92

## [1.1.1][] - 2019-03-22

[1.1.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.1.0...1.1.1

### Changed

- Fix a failure when no top-level controls were provided but an activity
  control was declared [#88][88]
- Warn when control Python package is not installed but do not fail experiment
  during validation [#90][90]. Controls should remain optional.

[88]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/88
[90]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/90


## [1.1.0][] - 2019-03-11

[1.1.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.0.0...1.1.0

#### Added

- a new tolerance type called `range` to support scenarios such as:

  value type is:
  ```
  {
      "status": 200,
      "headers": {"content-type": "text/plain"},
      "body": "1234.8"
  }
  ```

  tolerance is as follows:
  ```
  {
      "type": "range",
      "range": [1000.0, 2000.0]
      }
  }
  ```

  lower and upper bounds may be integers or floats.


## [1.0.0][] - 2019-02-21

[1.0.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.0.0rc3...1.0.0

### Changed

- Delint to clean things up before 1.0
- Do not pin too strictly or this causes havoc when updating chaoslib

## [1.0.0rc3][] - 2019-01-29

[1.0.0rc3]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.0.0rc2...1.0.0rc3

### Changed

- Fix differences of API between Vault KV secret v1 and v2 [#80][80]
- Catch Vault AppRole client error [#81][81]
- Support now [Service Account][serviceaccount] Vault authentication to access Vault secrets [#82][82]

[80]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/80
[81]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/81
[82]: https://github.com/chaostoolkit/chaostoolkit-lib/pull/82

## [1.0.0rc2][] - 2019-01-28

[1.0.0rc2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/1.0.0rc1...1.0.0rc2

### Changed

- Ensure Python control can be found [#63][63]
- Ensure activity is looked up before control is applied [#64][64]
- Ensure controls are applied only once before/after [#65][65]
- Declare the name property in the catch block of the python control
  validator [#66][66]
- Use `ImportError` exception instead of `ModuleNotFoundError` which is not
  declared in Python 3.5 [#67][67]
- Disallow empty JSON path [#68][68]
- Pass the experiment to each control when requested via the `experiment`
  parameter of the Python function [#69][69]
- Specify the [Vault KV secret][kvversion] default version to be used via the
  `"vault_kv_version"` configuration property, defaulting to v2
- Support now [AppRole][approle] Vault authentication to access Vault secrets
  thanks to @AlexShemeshWix [#74][74]
- [BREAKING] Vault secrets are now accessed via the `path` property [#77][77]
  instead of the `key` property as before. A warning message will be displayed.

    ```json
        {
            "k8s": {
                "mykey": {
                    "type": "vault",
                    "path": "foo/bar"
                }
            }
        }
    ```

  In that case, you get the whole secrets payload from Vault set to the `mykey`
  property. If you want a specific value from that payload, specify its key
  as follows:

    ```json
    {
        "k8s": {
            "mykey": {
                "type": "vault",
                "path": "foo/bar",
                "key": "mypassword"
            }
        }
    }
    ```
- Switch to `yaml.safe_load()` vs the unsafe `yaml.load()` to load YAML
  experiments [#78][78]

[63]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/63
[64]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/64
[65]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/65
[66]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/66
[67]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/67
[68]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/68
[69]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/69
[74]: https://github.com/chaostoolkit/chaostoolkit-lib/pull/74
[77]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/77
[78]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/78

[kvversion]: https://www.vaultproject.io/api/secret/kv/index.html
[approle]: https://www.vaultproject.io/api/auth/approle/index.html
[serviceaccount]: https://www.vaultproject.io/api/auth/kubernetes/index.html

## [1.0.0rc1][] - 2018-11-30

[1.0.0rc1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.22.2...1.0.0rc1

### Changed

- Let's get ready to roll 1.0.0
- Pinned dependency versions

## [0.22.2][] - 2018-11-30

[0.22.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.22.1...0.22.2

### Changed

* Remove `NoReturn` import as it is not available prior Python 3.6.5 [#90][90]

[90]: https://github.com/chaostoolkit/chaostoolkit/issues/90

## [0.22.1][] - 2018-11-29

[0.22.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.22.0...0.22.1

### Added

* Bug fix release for missing exporting the chaoslib/control package
* Exposing readme as markdown in https://pypi.org/

## [0.22.0][] - 2018-11-29

[0.22.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.21.0...0.22.0

### Added

-  listing installed Chaos Toolkit extensions [#64][64]
-  log (at DEBUG level) which Python file holds an activity or control provider
   function [#59][59]
-  add controls to provide entry points into the execution flow to perform
   out of band tasks such as tracing, monitoring or run's control [#84][84]
   Simply add a block such as:
    ```
    "controls": [
       {
            "name": "tracing",
            "provider": {
                "type": "python",
                "module": "chaostracing.control"
            }
        }
    ]
    ```
    At the experiment, steady-state and/or activity level. This would apply
    the `tracing` control before and after the element it is enclosed in.

    By default, a control defined at the experiment level will be applied
    before and after, if you want to limit to one or the other, use the
    `scope` property:

    ```
    "controls": [
       {
            "name": "tracing",
            "scope": "after",
            "provider": {
                "type": "python",
                "module": "chaostracing.control"
            }
        }
    ]
    ```

    By default, a control defined at the experiment level will be applied at
    all sub-levels. You can change that behavior like this:

    ```
    "controls": [
       {
            "name": "tracing",
            "automatic": false,
            "provider": {
                "type": "python",
                "module": "chaostracing.control"
            }
        }
    ]
    ```

[64]: https://github.com/chaostoolkit/chaostoolkit/issues/64
[59]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/59
[84]: https://github.com/chaostoolkit/chaostoolkit/issues/84

## [0.21.0][] - 2018-09-19

[0.21.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.20.1...0.21.0

### Added

-  add [codecov][] integration
-  add a new `"deviated"` flag to the journal to signal when the experiment ran
   fully but the steady state deviated after the experimental method was
   executed
-  add a new `RunFlowEvent.RunDeviated` declaration which can be used to
   signal when the experiment deviated. This can be sent in addition to the
   other events. This would allow subscribers to be notified when an experiment
   failed because the system deviated, while not being notified for any other
   failures that aborted the experiment run altogether [#56][56]
-  attempt to detect the encoding of the stdout/stderr streams of the process
   activities. This is only the case when either the [chardet][] or [cchardet][]
   packages are installed. When decoding does fail, raise an `ActivityFailed`
   exception

[codecov]: https://codecov.io/gh/chaostoolkit/chaostoolkit-lib
[#56]: https://github.com/chaostoolkit/chaostoolkit/issues/56
[chardet]: https://chardet.readthedocs.io/en/latest/
[cchardet]: https://github.com/PyYoshi/cChardet

### Changed

-  wording of the messages when the experiment deviated [#56][56]

## [0.20.1][] - 2018-08-24

[0.20.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.20.0...0.20.1

### Changed

- Pass an `Accept: application/json, application/x+yaml` header when fetching
  the experiment over HTTP

## [0.20.0][] - 2018-08-09

[0.20.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.19.0...0.20.0

### Changed

- renamed `FailedActivity` to a more active style: `ActivityFailed` [#17][17]

[17]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/17

### Added

- support for the `extensions` block. A sequence of extension objects which are
  free to contain any piece of data they need. Their only mandatory property
  is a `name` [#60][60]
- support for loading experiments from a remote endpoint using the HTTP protocol
  is now supported [#53][53]. Note that we do not perform any validation that
  the endpoint is safe, it's up to the user to be careful here (for instance
  by downloading the experiment using curl and reviewing it). We also do not
  tolerate self-signed endpoints for now.
- added an `auths` entry to the settings file so that it can be used when
  loading from a remote endpoint that requires credentials. For now, the
  credentials should be manually added but this may be addressed when [#65][65]
  is tackled, below is an example of such an entry:

    ```yaml
    auths:
      mydomain.com:
        type: basic
        value: XYZ
      otherdomain.com:
        type: bearer
        value: UIY
      localhost:8081:
        type: digest
        value: UIY
    ```

[53]: https://github.com/chaostoolkit/chaostoolkit/issues/53
[60]: https://github.com/chaostoolkit/chaostoolkit/issues/60
[65]: https://github.com/chaostoolkit/chaostoolkit/issues/65

## [0.19.0][] - 2018-07-05

[0.17.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.17.0...0.19.0

### Added

- jsonpath tolerance can now take an ̀`expect` property to compare the returned
  results with a given value (which is not really well supported in jsonpath
  when not dealing with arrays)
- Ability to save settings as well as load them.
- Display a warning to the user when a HTTP call (using the HTTP provider)
  returned a status code above 399. This makes it easier to track, during the
  experimental method or rollbacks, when the endpoint responded something
  we may not expected. During the steady state hypothesis checks, this warning
  is not displayed as this may be expected [#46][46]

[46]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/46

### Changed

- when the probe of the steady state hypothesis fails with a `FailedActivity`
  exception, we now say that the steady state hypothesis was not met. Before,
  it would simply bail the whole experiment very sadly

## [0.17.0][] - 2018-04-27

[0.17.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.16.0...0.17.0

### Added

-   Experiments can now be loaded from YAML as well [#54][54]

[54]: https://github.com/chaostoolkit/chaostoolkit/issues/54

## [0.16.0][] - 2018-04-13

[0.16.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.15.1...0.16.0

### Changed

-   HTTP provider can pass request body as JSON when
    `"Content-Type: application/json"` is passed in the `headers` object of
    the provider
-   Process provider can also take its arguments as a string now so you can pass
    the command line arguments as-is. This is needed because some commands do not
    respect POSIX and this fails with Python subprocess
-   Output a dict from process probes, with keys 'status', 'stdout' and 'stderr'.
    This is a first step to better tolerance checks on process probes. [#21][21]
-   Tolerance is richer now as well. If you provide a dictionary, it won't be
    considered only as a new probe to run. Instead, it will look for the `type`
    key. It's a follow-up of [#21][21]:

    - if type is `"probe"`, then it is considered a new probe to run as usual,
      and the status of the probe makes the status of the tolerance.
    - if type is `"regex"`, then a `pattern` key must also be present with
      a valid [Python regex][re]. If a `target` key is also present, it must
      indicate where to find the content to search for in the tested value.
      If the tested value comes from a process probe, the `target` key must be
      either `"stdout"` or `"stderr"`. If it is a HTTP probe,  the `target` key
      must be `"body"`. In all other cases, the tested value is checked as-is.
    - if type is `"jsonpath"`, then a `path` key must also be present with
      a valid [JSON Path][jp]. If a `target` key is also present, it must
      indicate where to find the content to search for in the tested value.
      If the tested value comes from a process probe, the `target` key must be
      either `"stdout"` or `"stderr"`. If it is a HTTP probe,  the `target` key
      must be `"body"`. In all other cases, the tested value is checked as-is.
      Note that, when the tested value is a string (no matter where read from),
      we try to parse it as a JSON payload first.
      Finally, you can provide a ̀`count` key as well, there are exactly that
      number of matches.


[21]: https://github.com/chaostoolkit/chaostoolkit/issues/21
[re]: https://docs.python.org/3/library/re.html#module-re
[jp]: https://github.com/h2non/jsonpath-ng

## [0.15.1][] - 2018-03-09

[0.15.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.15.0...0.15.1

### Changed

-   Log a message when loading the configuration
-   Raise `InvalidExperiment` when a configuration or secret references a key
    in the environment and that key does not exist (it may not be set however)
    [#40][40]. This bails the experiment at validation time so before it runs.

[40]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/40

## [0.15.0][] - 2018-02-20

[0.15.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.14.0...0.15.0

### Changed

-   Process activities can now take their arguments as a list rather than a
    dictionary. The rationale is that command line arguments sometimes need
    ordering and dictionaries only provided ordering (as in insertion ordering)
    only [since Python 3.6][ordereddict]. Assuming older versions of Python will
    eventually get it backported is not reasonable. Therefore, a list is more
    appropriate now and a warning message will be displayed when your experiment
    uses the dictionary approach. Notice that HTTP and Python activities will
    remain mapping only. [#34][34]
-   Added module to warn about deprecated features.
-   Added settings for the user-supplied configurations [#35][35]
-   Added event support [#33][33]

[33]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/33
[34]: https://github.com/chaostoolkit/chaostoolkit-lib/pull/34
[ordereddict]: https://stackoverflow.com/a/39980744/1363905
[35]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/35

## [0.14.0][] - 2018-02-06

[0.14.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.13.1...0.14.0

### Changed

-   Do not fail the discovery when an extension is missing the `__all__`
    attribute [#28][28]
-   Include extension activity arguments type when discovering
    extension [#19][19]

[19]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/19
[28]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/28

## [0.13.1][] - 2018-01-30

[0.13.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.13.0...0.13.1

### Changed

-   Steady stade is optional, so don't expect it here

## [0.13.0][] - 2018-01-28

[0.13.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.2...0.13.0

### Changed

-   HTTP provider must be able to connect to self-signed HTTPS endpoint [#25][25]
-   Steady state is now added to the generated json report

[25]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/25

## [0.12.2][] - 2018-01-24

[0.12.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.1...0.12.2

### Changed

-   missing hvac dependency should not break chaos with an exception [#23][23]

[23]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/23

## [0.12.1][] - 2018-01-20

[0.12.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.0...0.12.1

### Changed

-   yaml is not required in this package

## [0.12.0][] - 2018-01-20

[0.12.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.11.0...0.12.0

### Changed

- Various dependencies cleanups
- Added the DCO notice for contributors

## [0.11.0][] - 2018-01-17

[0.11.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.10.0...0.11.0

### Changed

- Steady state hypothesis is not mandatory when exploring [#18][18]

[18]: https://github.com/chaostoolkit/chaostoolkit/issues/18

## [0.10.0][] - 2018-01-16

[0.10.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.4...0.10.0

### Added

- New discovery of extension capabilities [#16][16]

### Changed

- Pinning ply dependency version to 3.4 to avoid random install failures [#8][8]

[8]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/8
[16]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/16

## [0.9.4][] - 2018-01-10

[0.9.4]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.3...0.9.4

### Changed

- Proper merge of secrets from the different supported loaders

## [0.9.3][] - 2018-01-09

[0.9.3]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.2...0.9.3

### Changed

- Do not forget to load inlined secrets

## [0.9.2][] - 2018-01-05

[0.9.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.1...0.9.2

### Changed

- HTTP probe header dict must be serialiable back to JSON

## [0.9.1][] - 2018-01-05

[0.9.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.0...0.9.1

### Removed

- HTTP activity will not check status code any longer [#10][10]
- Process activity will not check return code any longer [#10][10]

[10]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/10

## [0.9.0][] - 2018-01-05

[0.9.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.2...0.9.0

### Added

- Steady state is now run after the method as well [#19][19]
- Allow tolerance to be based on the HTTP status code of the probe [#20][20]

### Changed

- Logging when an activity runs in the background
- Pause after we capture the end time of an activity
- HTTP Probe now returns a dict with status code, headers and body of the
  response

[19]: https://github.com/chaostoolkit/chaostoolkit/issues/19
[20]: https://github.com/chaostoolkit/chaostoolkit/issues/20

## [0.8.2][] - 2017-12-18

[0.8.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.1...0.8.2

### Changed

- Missing transitive dependency "ply"

## [0.8.1][] - 2017-12-18

[0.8.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.0...0.8.1

### Changed

- Packaging up the dev requirements for install from the tarball

## [0.8.0][] - 2017-12-17

[0.8.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.7.0...0.8.0

### Added

- Substitution from configuration and secrets so values can be dynamically set
- The journal contains now a global status of the run

### Changed

- Pausing activity message is logged before the activity running message for
  better clarity
- Arguments are now substituted with their configuration and secrets values
  before being applied

## [0.7.0][] - 2017-12-12

[0.7.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.6.0...0.7.0

### Added

- Configuration schema support
- Lots of logging added at the DEBUG level
- [EXPERIMENTAL] Loading secrets froom HashiCorp vault

### Changed

- [BREAKING] Secrets from environment variable now respects the API and do not
  get detected by parsing the secret's value
- Better handling of the steady hypothesis not matching its expectations
  Now the experiment terminates cleanly

## [0.6.0][] - 2017-12-06

[0.6.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.5.1...0.6.0

### Changed

* [BREAKING]: The specification has changed in a non-compatible way. We are
  working towards a 1.0.0 version of the specification as the initial draft was
  merely to set the stage. The `method` has been simplified and there are no
  more `steady` and `close` probes, only probes. We also now define a steady
  state hypothesis that would fail the experiment should it not meet its
  expected state. Finally, we define a `rollbacks` entry so that experiments
  can revert changes they made

### Added

* Experiment captures now SIGINT and system exit signals and swallows them so
  the journal is returned and can be inspected
* Activities can be cached and referenced from within experiment


## [0.5.1][] - 2017-11-23

[0.5.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.5.0...0.5.1

### Changed

-   Do not shadow functions
-   Log full errors on debug level
-   Always pause even if activity failed


## [0.5.0][] - 2017-11-19

[0.5.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.4.0...0.5.0

### Changed

-   Split the inner of `run_experiment` into various functions for better
    composability
-   Pause before/after activity


## [0.4.0][] - 2017-10-18

[0.4.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.3.0...0.4.0

### Changed

-   Better logging

## [0.3.0][] - 2017-10-18

[0.3.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.2.0...0.3.0

### Added

-   An `expected_status` for HTTP probe to consider HTTP errors as expected in
    some cases

## [0.2.0][] - 2017-10-10

[0.2.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.1.1...0.2.0

### Added

-   A first draft to loading secrets from environment
-   Passing those secrets as a mapping to actions and probes expecting them
-   Added support for background activities
-   Dry mode support

### Removed

-   Unused layer module

## [0.1.1][] - 2017-10-06

[0.1.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.1.0...0.1.1

### Changed

-   Package up extra files when installed from source

## [0.1.0][] - 2017-10-06

[0.1.0]: https://github.com/chaostoolkit/chaostoolkit-lib/tree/0.1.0

### Added

-   Initial release
