raiseorlaunch
=============

.. image:: https://img.shields.io/pypi/v/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

.. image:: https://img.shields.io/pypi/pyversions/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

| Run-or-raise-application-launcher for i3 window manager.
| If a specified application is already running, it will just focus the
  window. If not, it will run the application.

| It's also possible to specify a workspace. That way only this
  workspace will be used to raise and launch.
| workspace\_auto\_back\_and\_forth - if enabled - remains functional.
| It's also possible to use the scratchpad.

You can specify a window class, instance and/or title.

raiseorlaunch is intended to be used with i3-shortcuts.

It depends on `i3-py <https://github.com/ziberna/i3-py>`__.

Installation
------------
raiseorlaunch is in `PyPI <https://pypi.python.org/pypi/raiseorlaunch/>`__, so you can just

::

    pip install raiseorlaunch

For Arch Linux users it's also available in the `AUR <https://aur.archlinux.org/packages/raiseorlaunch/>`__.


Usage and options
-----------------

::

    usage: raiseorlaunch [-h] [-i] [-w WORKSPACE] [-r] [-e COMMAND] [-c WM_CLASS]
                         [-s WM_INSTANCE] [-t WM_TITLE] [--version]

    Run-or-raise-application-launcher for i3 window manager.

    optional arguments:
      -h, --help            show this help message and exit
      -i, --ignore-case     ignore case.
      -w WORKSPACE, --workspace WORKSPACE
                            workspace to use.
      -r, --scratch         use scratchpad
      -e COMMAND, --exec COMMAND
                            command to execute. If omitted, -c, -s or -t will be
                            used (lower-case). Careful: The command will not be
                            checked prior to execution!
      -c WM_CLASS, --class WM_CLASS
                            the window class.
      -s WM_INSTANCE, --instance WM_INSTANCE
                            the window instance.
      -t WM_TITLE, --title WM_TITLE
                            the window title.
      --version             show program's version number and exit

Examples
--------

.. code:: shell

    raiseorlaunch -c Firefox -s Navigator

Run or raise Firefox.

.. code:: shell

    raiseorlaunch -w SL -c Sublime_text -s sublime_text -e subl

This uses the workspace SL for sublime text.

.. code:: shell

    raiseorlaunch -r -c SpeedCrunch

Here we raise or launch SpeedCrunch and use the scratchpad.


Known problems
--------------

Keybinds steal focus when fired. This can have a negative impact with
applications that listen to FocusOut events and hide. This is due to `how X
works <https://github.com/i3/i3/issues/2843#issuecomment-316173601>`__.

Example:
********

When using Guake Terminal with "Hide on lose focus" enabled, raiseorlaunch
behaves as if the undelying window is focused.
