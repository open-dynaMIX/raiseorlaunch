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

Installing it directly with the setup.py creates a script-entry-point that
adds ~150ms delay. This is not acceptable for this kind of application.

This can be prevented, if creating a wheel first and installing that (needs
`wheel <https://pypi.python.org/pypi/wheel>`__ and
`pip <https://pypi.python.org/pypi/pip>`__ installed):

.. code:: shell

    python setup.py bdist_wheel
    pip install ./dist/raiseorlaunch-${VERSION}-py2.py3-none-any.whl

You can also just run the script without installing it:

.. code:: shell

    python -m raiseorlaunch ${OPTIONS}

or:

.. code:: shell

    ./raiseorlaunch/__main__.py ${OPTIONS}

Usage and options
-----------------

::

    usage: raiseorlaunch [-h] [-c WM_CLASS] [-s WM_INSTANCE] [-t WM_TITLE]
                         [-e COMMAND] [-w WORKSPACE] [-r] [-i] [-d] [-v]

    Run-or-raise-application-launcher for i3 window manager.

    optional arguments:
      -h, --help            show this help message and exit
      -c WM_CLASS, --class WM_CLASS
                            the window class.
      -s WM_INSTANCE, --instance WM_INSTANCE
                            the window instance.
      -t WM_TITLE, --title WM_TITLE
                            the window title.
      -e COMMAND, --exec COMMAND
                            command to execute. If omitted, -c, -s or -t will be
                            used (lower-case). Careful: The command will not be
                            checked prior to execution!
      -w WORKSPACE, --workspace WORKSPACE
                            workspace to use.
      -r, --scratch         use scratchpad
      -i, --ignore-case     ignore case.
      -d, --debug           display debug messages.
      -v, --version         show program's version number and exit

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
behaves as if the underlying window is focused.
