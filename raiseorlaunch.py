#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
raiseorlaunch 0.1:
Run-or-raise-application-launcher for i3 window manager.
Depends on: python2-i3-git
"""


import argparse
import os
from distutils import spawn
import sys
from subprocess import call
try:
    import i3
except ImportError:
    print >> sys.stderr, ("\033[31;1mError: Module i3 not found. Please "
                          "install the package 'python2-i3-git'.\nMaybe this "
                          "package is called differently in your distribution."
                          "\nOr use i3-py from pip2."
                          " \033[0m")
    sys.exit(1)


def verify_app(parser, application):
    """
    Verify the given application argument.
    """
    def error_handle():
        """
        Handle a verify_app error.
        """
        parser.error("%s is not an executable!" % application)

    is_exe = spawn.find_executable(application)
    if is_exe is None:
        error_handle()
    elif is_exe is application:
        if not os.access(application, os.X_OK):
            error_handle()
    return application


def set_command(parser, args):
    """
    Set args.command, if --exec is omitted.
    In this order:
    class, instance, title.
    """
    if args.command is None:
        if args.wm_class:
            args.command = verify_app(parser, args.wm_class.lower())
        elif args.wm_instance:
            args.command = verify_app(parser, args.wm_instance.lower())
        elif args.wm_title:
            args.command = verify_app(parser, args.wm_titlef.lower())
    return args


def check_args(parser, args):
    """
    Verify that at least one argument is given.
    """
    if not args.wm_class and not args.wm_instance and not args.wm_title:
        parser.error("You need to specify one argument out of -c, -s or -t.")


def parse_arguments():
    """
    Parse all arguments.
    """
    parser = argparse.ArgumentParser(description=sys.argv[0],
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)

    parser.add_argument("-i", "--ignore-case", dest="ignore_case",
                              action="store_true", help="Ignore case.")

    parser.add_argument("-w", "--workspace", dest="workspace",
                              help="Workspace to use.")
    parser.set_defaults(workspace=None)

    parser.add_argument("-e", "--exec", dest="command",
                              help="Command to execute. If omitted, -c, -s or "
                              "-t will be used (lower-case). "
                              "Careful: The command will not be checked "
                              "prior to execution!")
    parser.set_defaults(command=None)

    parser.add_argument("-c", "--class", dest="wm_class",
                              help="The window class.")
    parser.set_defaults(wm_class=None)

    parser.add_argument("-s", "--instance", dest="wm_instance",
                              help="The window instance.")
    parser.set_defaults(wm_instance=None)

    parser.add_argument("-t", "--title", dest="wm_title",
                              help="The window title.")
    parser.set_defaults(wm_title=None)

    args = parser.parse_args()

    check_args(parser, args)

    config = set_command(parser, args)

    return config


def do_focus(config):
    """
    Do the focussing of the window.
    """
    if config.ignore_case:
        if config.wm_class:
            config.wm_class = "(?i)" + config.wm_class
        if config.wm_instance:
            config.wm_instance = "(?i)" + config.wm_instance
        if config.wm_title:
            config.wm_title = "(?i)" + config.wm_title

    focus_args = {}
    if config.wm_class:
        focus_args['Class'] = config.wm_class
    if config.wm_instance:
        focus_args['Instance'] = config.wm_instance
    if config.wm_title:
        focus_args['title'] = config.wm_title

    i3.focus(**focus_args)


def switch_ws(config):
    """
    Do the switching of the workspace.
    """
    i3.command('workspace', config.workspace)


def get_window_tree(workspace):
    """
    Get the current window tree.
    """
    # If a workspace is specified, only check for windows on the specified
    # workspace.
    if workspace:
        temptree = i3.filter(name=workspace)
        if temptree == []:
            return None
        tree = i3.filter(tree=temptree, nodes=[])
        for floatlist in temptree[0]['floating_nodes']:
            for float in floatlist['nodes']:
                tree.append(float)
    else:
        tree = i3.filter(nodes=[])
        for subtree in tree:
            for floatlist in subtree['floating_nodes']:
                for float in floatlist['nodes']:
                    tree.append(float)
    return tree


def is_running(config):
    """
    Check if application is running on the (maybe) given workspace.
    """
    tree = get_window_tree(config.workspace)
    if not tree:
        return False

    # Iterate over the windows
    for window in tree:
        if 'window_properties' in window:
            if config.ignore_case:
                wm_class = window['window_properties']['class'].lower()
                wm_instance = window['window_properties']['instance'].lower()
                wm_title = window['window_properties']['title'].lower()
                if config.wm_class:
                    config.wm_class = config.wm_class.lower()
                if config.wm_instance:
                    config.wm_instance = config.wm_instance.lower()
                if config.wm_title:
                    config.wm_title = config.wm_title.lower()
            else:
                wm_class = window['window_properties']['class']
                wm_instance = window['window_properties']['instance']
                wm_title = window['window_properties']['title']

            if config.wm_class:
                if config.wm_class not in wm_class:
                    continue
            if config.wm_instance:
                if config.wm_instance not in wm_instance:
                    continue
            if config.wm_title:
                if config.wm_title not in wm_title:
                    continue
            return True
    return False


def run_command(command):
    """
    Run the specified command.
    """
    call(command, shell=True)


def get_current_ws():
    """
    Get the current workspace name.
    """
    for ws in i3.get_workspaces():
        if ws['visible']:
            return ws['name']


def main():
    config = parse_arguments()

    if config.workspace:
        if is_running(config):
            current_ws_old = get_current_ws()
            do_focus(config)
            if current_ws_old == config.workspace:
                switch_ws(config)
        else:
            if not get_current_ws() == config.workspace:
                switch_ws(config)
            run_command(config.command)
    else:
        if is_running(config):
            current_ws_old = get_current_ws()
            do_focus(config)
            current_ws_new = get_current_ws()
            if current_ws_old == current_ws_new:
                config.workspace = current_ws_new
                switch_ws(config)
        else:
            run_command(config.command)


if __name__ == "__main__":
    main()
