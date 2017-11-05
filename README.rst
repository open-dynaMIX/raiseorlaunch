raiseorlaunch
=============

.. image:: https://img.shields.io/pypi/v/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

.. image:: https://img.shields.io/pypi/pyversions/raiseorlaunch.svg
      :target: https://pypi.python.org/pypi/raiseorlaunch/

A run-or-raise-application-launcher for i3 window manager.

If a specified application is already running, it will just focus it's
window. If not, it will run the application.

It's also possible to specify a workspace or the scratchpad. That way only
this workspace will be used to raise and launch.

workspace\_auto\_back\_and\_forth (if enabled) remains functional.

You can specify a window class, instance and/or title.

raiseorlaunch is intended to be used with i3-shortcuts.

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

- `i3-py <https://github.com/ziberna/i3-py>`__

Install
~~~~~~~~~~~~

Installing it directly with the setup.py creates a script-entry-point that
adds ~150ms delay. This is not acceptable for this kind of application.

This can be prevented, if creating a wheel first and installing that (needs
`wheel <https://pypi.python.org/pypi/wheel>`__ and
`pip <https://pypi.python.org/pypi/pip>`__):

.. code:: shell

    python setup.py bdist_wheel
    pip install ./dist/raiseorlaunch-${VERSION}-py2.py3-none-any.whl

Run without installation
~~~~~~~~~~~~~~~~~~~~~~~~

You can also just run raiseorlaunch without installing it:

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

    A run-or-raise-application-launcher for i3 window manager.

    optional arguments:
      -h, --help            show this help message and exit
      -c WM_CLASS, --class WM_CLASS
                            the window class
      -s WM_INSTANCE, --instance WM_INSTANCE
                            the window instance
      -t WM_TITLE, --title WM_TITLE
                            the window title
      -e COMMAND, --exec COMMAND
                            command to execute. If omitted, -c, -s or -t will be
                            used (lower-case). Careful: The command will not be
                            checked prior to execution!
      -w WORKSPACE, --workspace WORKSPACE
                            workspace to use
      -r, --scratch         use scratchpad
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

Use the workspace SL for sublime text:

.. code:: shell

    raiseorlaunch -w SL -c Sublime_text -s sublime_text -e subl

Raise or launch SpeedCrunch and use the scratchpad.

.. code:: shell

    raiseorlaunch -r -c SpeedCrunch

i3 bindsym
**********

In i3 config you can define a bindsym like that:

.. code::

    bindsym ${KEYS} exec --no-startup-id raiseorlaunch ${OPTIONS}

e.g.

.. code::

    bindsym $mod+s exec --no-startup-id raiseorlaunch -w SL -c Sublime_text -s sublime_text -e subl

for binding `$mod+s` to raise or launch sublime text.


Known problems
--------------

Keybinds steal focus when fired. This can have a negative impact with
applications that listen to FocusOut events and hide. This is due to `how X
works <https://github.com/i3/i3/issues/2843#issuecomment-316173601>`__.

Example:
********

When using Guake Terminal with "Hide on lose focus" enabled, raiseorlaunch
behaves as if the underlying window is focused.
