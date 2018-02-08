raiseorlaunch
=============

.. image:: https://img.shields.io/pypi/v/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

.. image:: https://img.shields.io/pypi/pyversions/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

A run-or-raise-application-launcher for
`i3 window manager <https://i3wm.org/>`__.

Features
--------

- If a provided application is running, focus it's window, otherwise run it
- Provide a regex for window class, instance and/or title to compare with
  running windows
- Optionally enable case-insensitive comparison
- Optionally provide a workspace to use for raising and running
- Optionally use the scratchpad for raising and running
- Optionally provide a con_mark for raising and running
- workspace\_auto\_back\_and\_forth (if enabled) remains functional

Installation
------------

Repositories
************

raiseorlaunch is in `PyPI <https://pypi.python.org/pypi/raiseorlaunch/>`__,
so you can just

::

    pip install raiseorlaunch

For Arch Linux users it's also available in the
`AUR <https://aur.archlinux.org/packages/raiseorlaunch/>`__.

Manual
******

Dependencies
~~~~~~~~~~~~

- python3
- `i3ipc-python <https://github.com/acrisci/i3ipc-python>`__

Install
~~~~~~~~~~~~

Installing it directly with the setup.py creates a script-entry-point that
adds ~150ms delay. That's not acceptable for this kind of application.

This can be prevented, if creating a wheel first and installing that (needs
`wheel <https://pypi.python.org/pypi/wheel>`__ and
`pip <https://pypi.python.org/pypi/pip>`__):

.. code:: shell

    python setup.py bdist_wheel
    pip install ./dist/raiseorlaunch-${VERSION}-py3-none-any.whl

Run without installation
~~~~~~~~~~~~~~~~~~~~~~~~

You can also just run raiseorlaunch without installing it:

.. code:: shell

    python -m raiseorlaunch ${ARGUMENTS}

or:

.. code:: shell

    ./raiseorlaunch/__main__.py ${ARGUMENTS}

Usage and options
-----------------

::

    usage: raiseorlaunch [-h] [-c WM_CLASS] [-s WM_INSTANCE] [-t WM_TITLE]
                         [-e COMMAND] [-w WORKSPACE] [-r] [-m CON_MARK]
                         [-l EVENT_TIME_LIMIT] [-i] [-d] [-v]

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
      -r, --scratch         use scratchpad
      -m CON_MARK, --mark CON_MARK
                            con_mark to use when raising and set when launching
      -l EVENT_TIME_LIMIT, --event-time-limit EVENT_TIME_LIMIT
                            Time limit in seconds to listen to window events when
                            using the scratchpad. Defaults to 2.
      -i, --ignore-case     ignore case when comparing
      -d, --debug           display debug messages
      -v, --version         show program's version number and exit

Examples
--------

CLI
***

Run or raise Firefox:

.. code:: shell

    raiseorlaunch -c Firefox -s Navigator

Use the workspace `SL` for sublime text:

.. code:: shell

    raiseorlaunch -w SL -c "^Sublime" -s sublime_text -e subl

Raise or launch SpeedCrunch and use the scratchpad:

.. code:: shell

    raiseorlaunch -r -c SpeedCrunch

Use a script to start application:

.. code:: shell

    raiseorlaunch -r -c SpeedCrunch -e "--no-startup-id /path/to/my-cool-script.sh"

Raise the window with the con_mark `wiki`. If not found, execute command and
mark the new window matching the provided properties. Set the time limit to
wait for a new window to 3 seconds:

.. code:: shell

    raiseorlaunch -c Firefox -s Navigator -e "firefox --new-window https://wiki.archlinux.org/" -m wiki -l 3

i3 bindsym
**********

In i3 config you can define a bindsym like that:

.. code::

    bindsym ${KEYS} exec --no-startup-id raiseorlaunch ${ARGUMENTS}

e.g.

.. code::

    bindsym $mod+s exec --no-startup-id raiseorlaunch -w SL -c "^Sublime" -s sublime_text -e subl

for binding `$mod+s` to raise or launch sublime text.

Quotation marks
---------------
The command will not be quoted when calling `exec`. Make sure you properly escape any needed quotation marks. For simple commands there is no need to do anything.

Known problems
--------------

Keybindings steal focus when fired. This can have a negative impact with
applications that listen to FocusOut events and hide. This is due to `how X
works <https://github.com/i3/i3/issues/2843#issuecomment-316173601>`__.

Example:
********

When using Guake Terminal with "Hide on lose focus" enabled, raiseorlaunch
behaves as if the underlying window is focused.
