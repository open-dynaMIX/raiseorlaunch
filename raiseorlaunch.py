#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run-or-raise-application-launcher for i3 window manager.
"""


from __future__ import print_function


__title__ = 'raiseorlaunch'
__description__ = 'Run-or-raise-application-launcher for i3 window manager.'
__version__ = '0.1.0'
__license__ = 'MIT'
__author__ = 'Fabio Rämi'


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
    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)

    parser.add_argument("-i", "--ignore-case", dest="ignore_case",
                        action="store_true", help="ignore case.")

    parser.add_argument("-w", "--workspace", dest="workspace",
                        help="workspace to use.")
    parser.set_defaults(workspace=None)

    parser.add_argument("-r", "--scratch", dest="scratch",
                        action="store_true", help="use scratchpad")

    parser.add_argument("-e", "--exec", dest="command",
                        help="command to execute. If omitted, -c, -s or "
                        "-t will be used (lower-case). "
                        "Careful: The command will not be checked "
                        "prior to execution!")
    parser.set_defaults(command=None)

    parser.add_argument("-c", "--class", dest="wm_class",
                              help="the window class.")
    parser.set_defaults(wm_class='')

    parser.add_argument("-s", "--instance", dest="wm_instance",
                        help="the window instance.")
    parser.set_defaults(wm_instance='')

    parser.add_argument("-t", "--title", dest="wm_title",
                        help="the window title.")
    parser.set_defaults(wm_title='')

    parser.add_argument('--version', action='version',
                        version=__version__)

    args = parser.parse_args()

    check_args(parser, args)

    args = set_command(parser, args)

    return args


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


def compare_running(c_wm_class, wm_class,
                    c_wm_instance, wm_instance,
                    c_wm_title, wm_title,
                    ignore_case):
    if ignore_case:
        c_wm_class = c_wm_class.lower()
        wm_class = wm_class.lower()
        c_wm_instance = c_wm_instance.lower()
        wm_instance = wm_instance.lower()
        c_wm_title = c_wm_title.lower()
        wm_title = wm_title.lower()

    if c_wm_class:
        if not c_wm_class == wm_class:
            return False
    if c_wm_instance:
        if not c_wm_instance == wm_instance:
            return False
    if c_wm_title:
        if not c_wm_title == wm_title:
            return False
    return True


def get_running_ids(args):
    """
    Check if application is running on the (maybe) given workspace.
    """
    running = {'id': None, 'scratch_id': None, 'focused': None}
    tree = get_window_tree(args.workspace)
    if not tree:
        return running

    # Iterate over the windows
    for window in tree:
        if 'window_properties' in window:
            wm_class = window['window_properties']['class']
            wm_instance = window['window_properties']['instance']
            if 'title' in window['window_properties']:
                wm_title = window['window_properties']['title']
            else:
                wm_title = ''

            if not compare_running(args.wm_class, wm_class,
                                   args.wm_instance, wm_instance,
                                   args.wm_title, wm_title,
                                   args.ignore_case):
                continue

            if 'scratch_id' in window:
                running['scratch_id'] = window['scratch_id']

            running['id'] = window['window']
            running['focused'] = window['focused']

    return running


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


def main():
    args = parse_arguments()

    running = get_running_ids(args)
    if args.workspace:
        if running['id']:
            current_ws_old = get_current_ws()

            if not running['focused']:
                i3.focus(id=running['id'])
            else:
                if current_ws_old == args.workspace:
                    switch_ws(args.workspace)
        else:
            if not get_current_ws() == args.workspace:
                switch_ws(args.workspace)
            run_command(args.command)
    else:
        if running['id']:
            if args.scratch:
                i3.command('[id={}]'.format(running['id']),
                           'scratchpad',
                           'show')
            else:
                current_ws_old = get_current_ws()
                if not running['focused']:
                    i3.focus(id=running['id'])
                else:
                    if current_ws_old == get_current_ws():
                        if not running['scratch_id']:
                            switch_ws(current_ws_old)
        else:
            run_command(args.command)
            if args.scratch:
                sleep(1.5)
                running = get_running_ids(args)
                i3.command('[id={}]'.format(running['id']), 'move',
                           'scratchpad')
                i3.command('[id={}]'.format(running['id']), 'scratchpad',
                           'show')


if __name__ == "__main__":
    main()
