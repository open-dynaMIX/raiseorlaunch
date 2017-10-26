#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run-or-raise-application-launcher for i3 window manager.
"""

from __future__ import print_function
import sys
import argparse
import os
from distutils import spawn
from subprocess import Popen
from time import sleep
try:
    import i3
except ImportError:
    print("\033[31;1mError: Module i3 not found.\033[0m", file=sys.stderr)
    sys.exit(1)


description = 'Run-or-raise-application-launcher for i3 window manager.'


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
    if not is_exe:
        error_handle()
    elif is_exe == application:
        if not os.access(application, os.X_OK):
            error_handle()
    return application


def set_command(parser, args):
    """
    Set args.command, if --exec is omitted.
    In this order:
    class, instance, title.
    """
    if not args.command:
        if args.wm_class:
            args.command = verify_app(parser, args.wm_class.lower())
        elif args.wm_instance:
            args.command = verify_app(parser, args.wm_instance.lower())
        elif args.wm_title:
            args.command = verify_app(parser, args.wm_titlef.lower())
    else:
        verify_app(parser, args.command.split(' ')[0])
    return args


def check_args(parser, args):
    """
    Verify that at least one argument is given.
    """
    if not args.wm_class and not args.wm_instance and not args.wm_title:
        parser.error("You need to specify one argument out of -c, -s or -t.")
    if args.scratch and args.workspace:
        parser.error("You cannot use the scratchpad on a specific workspace.")


def parse_arguments():
    """
    Parse all arguments.
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)

    parser.add_argument("-i", "--ignore-case", dest="ignore_case",
                              action="store_true", help="Ignore case.")

    parser.add_argument("-w", "--workspace", dest="workspace",
                              help="Workspace to use.")
    parser.set_defaults(workspace=None)

    parser.add_argument("-r", "--scratch", dest="scratch",
                              action="store_true", help="Use scratchpad")

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


def switch_ws(workspace):
    """
    Do the switching of the workspace.
    """
    i3.command('workspace', workspace)


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
                if floatlist['scratchpad_state'] == "none":
                    for float in floatlist['nodes']:
                        tree.append(float)
                else:
                    scratch_id = floatlist['id']
                    for float in floatlist['nodes']:
                        float['scratch_id'] = scratch_id
                        tree.append(float)
    return tree


def is_running(config):
    """
    Check if application is running on the (maybe) given workspace.
    """
    tree = get_window_tree(config.workspace)
    if not tree:
        return [False]

    # Iterate over the windows
    for window in tree:
        if 'window_properties' in window:
            if config.ignore_case:
                wm_class = window['window_properties']['class'].lower()
                wm_instance = window['window_properties']['instance'].lower()
                if 'title' in window['window_properties']:
                    wm_title = window['window_properties']['title'].lower()
                else:
                    wm_title = None
                if config.wm_class:
                    config.wm_class = config.wm_class.lower()
                if config.wm_instance:
                    config.wm_instance = config.wm_instance.lower()
                if config.wm_title:
                    config.wm_title = config.wm_title.lower()
            else:
                wm_class = window['window_properties']['class']
                wm_instance = window['window_properties']['instance']
                if 'title' in window['window_properties']:
                    wm_title = window['window_properties']['title']
                else:
                    wm_title = None

            if config.wm_class:
                if config.wm_class not in wm_class:
                    continue
            if config.wm_instance:
                if config.wm_instance not in wm_instance:
                    continue
            if config.wm_title:
                if config.wm_title not in wm_title:
                    continue
            if 'scratch_id' not in window:
                window['scratch_id'] = None
            return window['window'], window['scratch_id']
    return [False]


def run_command(command):
    """
    Run the specified command.
    """
    Popen(command, shell=True)


def get_current_ws():
    """
    Get the current workspace name.
    """
    for ws in i3.get_workspaces():
        if ws['focused']:
            return ws['name']


def compile_scratch_props(config):
    returnstr = "["
    if config.wm_class:
        returnstr += "class=" + config.wm_class
    if config.wm_instance:
        returnstr += ", instance=" + config.wm_instance
    if config.wm_title:
        returnstr += ", title=" + config.wm_title
    returnstr += "]"

    return returnstr


def main():
    config = parse_arguments()

    is_running_ret = is_running(config)
    if config.workspace:
        if is_running_ret[0]:
            current_ws_old = get_current_ws()
            i3.focus(id=is_running_ret[0])
            if current_ws_old == config.workspace:
                switch_ws(config.workspace)
        else:
            if not get_current_ws() == config.workspace:
                switch_ws(config.workspace)
            run_command(config.command)
    else:
        if is_running_ret[0]:
            if config.scratch:
                i3.command(compile_scratch_props(config), 'scratchpad', 'show')
            else:
                current_ws_old = get_current_ws()
                i3.focus(id=is_running_ret[0])
                if current_ws_old == get_current_ws()and not is_running_ret[1]:
                    switch_ws(current_ws_old)
        else:
            run_command(config.command)
            if config.scratch:
                sleep(1.5)
                i3.command(compile_scratch_props(config), 'move',
                           'scratchpad')
                i3.command(compile_scratch_props(config), 'scratchpad',
                           'show')


if __name__ == "__main__":
    main()
