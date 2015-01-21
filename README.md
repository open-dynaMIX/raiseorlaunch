# raiseorlaunch

Run-or-raise-application-launcher for i3.
If a specified application is already running, it will just focus the windows.
Else it will run the application.

It's also possible to specify a workspace. That way only this workspace will
be used to raise or launch.

You can specify a window class, instance and/or title.

raiseorlaunch is intended to be used with i3-shortcuts.

It depends on i3-py (https://github.com/ziberna/i3-py or - for Arch Linux -
  https://aur.archlinux.org/packages/python2-i3-git)


  ## Invocation

  Usage:

  raiseorlaunch [-h] [-i] [-w WORKSPACE] [-e COMMAND]
  [-c WM_CLASS] [-s WM_INSTANCE] [-t WM_TITLE]

  Options:

  -h, --help
  show this help message and exit
  -i, --ignore-case
  Ignore case.
  -w WORKSPACE, --workspace WORKSPACE
  Workspace to use.
  -e COMMAND, --exec COMMAND
  Command to execute. If omitted, -c, -s
  or -t will be used (lower-case).
  Careful: The command will not be
  checked prior to execution!
  -c WM_CLASS, --class WM_CLASS
  The window class.
  -s WM_INSTANCE, --instance WM_INSTANCE
  The window instance.
  -t WM_TITLE, --title WM_TITLE
  The window title.
