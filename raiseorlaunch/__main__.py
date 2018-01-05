#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the CLI for raiseorlaunch. A run-or-raise-application-launcher
for i3 window manager.
"""

import os
import argparse
from distutils import spawn
import logging
from raiseorlaunch import (Raiseorlaunch, RaiseorlaunchWorkspace,
                           __title__, __version__, __description__)


logger = logging.getLogger(__name__)


def verify_app(parser, application):
    """
    Verify the executable if not provided with -e.
    """
    def error_handle():
        """
        Handle a verify_app error.
        """
        parser.error('{} is not an executable! Did you forget to supply -e?'
                     .format(application))

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
        for i in ['wm_class', 'wm_instance', 'wm_title']:
            if getattr(args, i):
                args.command = getattr(args, i).lower()
                break

        if not args.command:
            parser.error('No executable provided!')
        verify_app(parser, args.command)
        logger.debug('Set command to: {}'.format(args.command))

    return args


def check_args(parser, args):
    """
    Verify that at least one argument is given.
    """
    if args.scratch and args.workspace:
        parser.error('You cannot use the scratchpad on a specific workspace.')


def parse_arguments():
    """
    Parse all arguments.
    """
    parser = argparse.ArgumentParser(prog=__title__,
                                     description=__description__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)

    parser.add_argument('-c', '--class', dest='wm_class',
                        help='the window class regex')
    parser.set_defaults(wm_class='')

    parser.add_argument('-s', '--instance', dest='wm_instance',
                        help='the window instance regex')
    parser.set_defaults(wm_instance='')

    parser.add_argument('-t', '--title', dest='wm_title',
                        help='the window title regex')
    parser.set_defaults(wm_title='')

    parser.add_argument('-e', '--exec', dest='command',
                        help='command to run with exec. If omitted, -c, -s or '
                        '-t will be used (lower-case). The command will '
                        'always be quoted, so make sure you properly escape '
                        'internal quotation marks. If using double-quotes '
                        'for "-e", you need to triple escape them, if using '
                        'single-quotes only one is needed. Careful: The '
                        'command will not be checked prior to execution!')
    parser.set_defaults(command=None)

    parser.add_argument('--no-startup-id', dest='no_startup_id',
                        action='store_true',
                        help='use --no-startup-id when running command with '
                        'exec')

    parser.add_argument('-w', '--workspace', dest='workspace',
                        help='workspace to use')
    parser.set_defaults(workspace=None)

    parser.add_argument('-r', '--scratch', dest='scratch',
                        action='store_true', help='use scratchpad')

    parser.add_argument('-i', '--ignore-case', dest='ignore_case',
                        action='store_true', help='ignore case when comparing')

    parser.add_argument('-d', '--debug', dest='debug',
                        help='display debug messages',
                        action='store_true')

    parser.add_argument('-v', '--version', action='version',
                        version=__version__)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    check_args(parser, args)

    args = set_command(parser, args)

    return args, parser


def main():
    """
    Main CLI function for raiseorlaunch.
    """
    args, parser = parse_arguments()

    logger.debug('Provided arguments: {}'.format(args))

    try:
        if not args.workspace:
            rol = Raiseorlaunch(command=args.command,
                                wm_class=args.wm_class,
                                wm_instance=args.wm_instance,
                                wm_title=args.wm_title,
                                ignore_case=args.ignore_case,
                                no_startup_id=args.no_startup_id,
                                scratch=args.scratch)
        else:
            rol = RaiseorlaunchWorkspace(command=args.command,
                                         wm_class=args.wm_class,
                                         wm_instance=args.wm_instance,
                                         wm_title=args.wm_title,
                                         ignore_case=args.ignore_case,
                                         no_startup_id=args.no_startup_id,
                                         workspace=args.workspace)
    except TypeError as e:
        if str(e) == ('You need to specify '
                      '"wm_class", "wm_instance" or "wm_title".'):
            parser.error('You need to specify at least one argument out '
                         'of -c, -s or -t.')
        else:
            raise

    rol.run()


if __name__ == '__main__':
    main()
