# raiseorlaunch

[![PyPI](https://img.shields.io/pypi/v/raiseorlaunch.svg)](https://pypi.org/project/raiseorlaunch/)
[![Python versions](https://img.shields.io/pypi/pyversions/raiseorlaunch.svg)](https://pypi.org/project/raiseorlaunch/)
[![Build Status](https://travis-ci.com/open-dynaMIX/raiseorlaunch.svg?branch=master)](https://travis-ci.com/open-dynaMIX/raiseorlaunch)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/open-dynaMIX/raiseorlaunch/blob/master/.coveragerc#L9)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/github/license/open-dynaMIX/raiseorlaunch.svg)](https://opensource.org/licenses/MIT)

A run-or-raise-application-launcher for [i3 window manager](https://i3wm.org/).

## Features

 - If a provided application is running, focus it's window, otherwise
   run it
 - Provide a regex for window class, instance and/or title to compare
   with running windows
 - Optionally enable case-insensitive comparison
 - Optionally provide a workspace to use for raising and running
 - Optionally provide an initial workspace to run the application
 - Optionally use the scratchpad for raising and running
 - Optionally provide a con_mark for raising and running
 - workspace_auto_back_and_forth (if enabled) remains functional
 - Optionally cycle through matching windows (this will break
   workspace_auto_back_and_forth if more than one window matches
   the given properties)
 - Optionally leave fullscreen on target workspace
 - Created windows will always be moved to the expected workspace. This
   fixes the behaviour of applications that don't implement
   startup-notifications. By default this works for windows created
   within 2 seconds. The timeout is configurable with
   `-l/--event-time-limit`

## Installation

### Repositories

raiseorlaunch is in [PyPI](https://pypi.org/project/raiseorlaunch/),
so you can just

    pip install raiseorlaunch

For Arch Linux users it's also available in the
[AUR](https://aur.archlinux.org/packages/raiseorlaunch/).

### Manual

#### Dependencies

-   python3 or pypy3
-   [i3ipc-python](https://github.com/acrisci/i3ipc-python)

#### Install

Installing it directly with the setup.py creates a script-entry-point
that adds ~150ms delay. That's not acceptable for this kind of
application.

This can be prevented, if creating a wheel first and installing that
(needs [wheel](https://pypi.org/project/wheel) and
[pip](https://pypi.org/project/pip)):

``` shell
python setup.py bdist_wheel
pip install ./dist/raiseorlaunch-${VERSION}-py3-none-any.whl
```

#### Run without installation

You can also just run raiseorlaunch without installing it:

``` shell
python -m raiseorlaunch ${ARGUMENTS}
```

or:

``` shell
./raiseorlaunch/__main__.py ${ARGUMENTS}
```

## Usage and options

```
usage: raiseorlaunch [-h] [-c WM_CLASS] [-s WM_INSTANCE] [-t WM_TITLE]
                     [-e COMMAND] [-w WORKSPACE | -W TARGET_WORKSPACE | -r]
                     [-m CON_MARK] [-l EVENT_TIME_LIMIT] [-i] [-C] [-f] [-d]
                     [-v]

A run-or-raise-application-launcher for i3 window manager.

optional arguments:
  -h, --help            show this help message and exit
  -c WM_CLASS, --class WM_CLASS
                        the window class regex
  -s WM_INSTANCE, --instance WM_INSTANCE
                        the window instance regex
  -t WM_TITLE, --title WM_TITLE
                        the window title regex
  -e COMMAND, --exec COMMAND
                        command to run with exec. If omitted, -c, -s or -t
                        will be used (lower-case). Careful: The command will
                        not be checked prior to execution!
  -w WORKSPACE, --workspace WORKSPACE
                        workspace to use
  -W TARGET_WORKSPACE, --target-workspace TARGET_WORKSPACE, --init-workspace TARGET_WORKSPACE
                        target workspace
  -r, --scratch         use scratchpad
  -m CON_MARK, --mark CON_MARK
                        con_mark to use when raising and set when launching
  -l EVENT_TIME_LIMIT, --event-time-limit EVENT_TIME_LIMIT
                        Time limit in seconds to listen to window events after
                        exec. Defaults to 2
  -i, --ignore-case     ignore case when comparing
  -C, --cycle           cycle through matching windows (this will break
                        workspace_back_and_forth if more than one window
                        matches the given properties)
  -f, --leave-fullscreen
                        Leave fullscreen on target workspace
  -d, --debug           display debug messages
  -v, --version         show program's version number and exit

```

## Examples

### CLI

Run or raise Firefox:

``` shell
raiseorlaunch -c Firefox -s Navigator
```

Use the workspace `SL` for sublime text:

``` shell
raiseorlaunch -w SL -c "^Sublime" -s sublime_text -e subl
```

Raise or launch SpeedCrunch and use the scratchpad:

``` shell
raiseorlaunch -r -c SpeedCrunch
```

Use a script to start application:

``` shell
raiseorlaunch -r -c SpeedCrunch -e "--no-startup-id /path/to/my-cool-script.sh"
```

Raise the window with the con_mark `wiki`. If not found,
execute command and mark the new window matching the provided
properties. Set the time limit to wait for a new window to 3 seconds:

``` shell
raiseorlaunch -c Firefox -s Navigator -e "firefox --new-window https://wiki.archlinux.org/" -m wiki -l 3
```

### i3 bindsym

In i3 config you can define a bindsym like that:

```
bindsym ${KEYS} exec --no-startup-id raiseorlaunch ${ARGUMENTS}
```

e.g.

```
bindsym $mod+s exec --no-startup-id raiseorlaunch -w SL -c "^Sublime" -s sublime_text -e subl
```

for binding `$mod+s` to raise or launch sublime text.

## Quotation marks

The command will not be quoted when calling `exec`. Make
sure you properly escape any needed quotation marks. For simple commands
there is no need to do anything.

## Known problems

Keybindings steal focus when fired. This can have a negative impact with
applications that listen to FocusOut events and hide. This is due to
[how X works](https://github.com/i3/i3/issues/2843#issuecomment-316173601).

### Example:

When using Guake Terminal with "Hide on lose focus" enabled,
raiseorlaunch behaves as if the underlying window is focused.
