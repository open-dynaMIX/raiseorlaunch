#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is the CLI for raiseorlaunch. A run-or-raise-application-launcher
for i3 window manager.
"""

import os
import argparse
from distutils import spawn
import logging
from raiseorlaunch import (Raiseorlaunch, RaiseorlaunchError,
                           __title__, __version__, __description__)


logger = logging.getLogger(__name__)


def verify_app(parser, application):
    """
    Verify the executable if not provided with -e.
    """
    def raise_exception():
        """
        Raise a parser error.
        """
        parser.error('{} is not an executable! Did you forget to supply -e?'
                     .format(application))

    is_exe = spawn.find_executable(application)
    if not is_exe:
        raise_exception()
    elif is_exe == application:
        if not os.access(application, os.X_OK):
            raise_exception()
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


def check_positive(value):
    def raise_exception():
        """
        Raise an ArgumentTypeError.
        """
        raise argparse.ArgumentTypeError('{} is not a positive integer or '
                                         'float'.format(value))
    try:
        fvalue = float(value)
    except ValueError:
        raise_exception()
    if fvalue <= 0:
        raise_exception()
    return fvalue


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

    parser.add_argument('-s', '--instance', dest='wm_instance',
                        help='the window instance regex')

    parser.add_argument('-t', '--title', dest='wm_title',
                        help='the window title regex')

    parser.add_argument('-e', '--exec', dest='command',
                        help='command to run with exec. If omitted, -c, -s or '
                        '-t will be used (lower-case). '
                        'Careful: The command will not be checked '
                        'prior to execution!')
    parser.set_defaults(command=None)

    parser.add_argument('-w', '--workspace', dest='workspace',
                        help='workspace to use')

    parser.add_argument('-r', '--scratch', dest='scratch',
                        action='store_true', help='use scratchpad')

    parser.add_argument('-m', '--mark', dest='con_mark',
                        help='con_mark to use when raising and set when '
                        'launching')

    parser.add_argument('-l', '--event-time-limit', dest='event_time_limit',
                        type=check_positive, help='Time limit in seconds to '
                        'listen to window events when using the scratchpad. '
                        'Defaults to 2.')

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

    args = set_command(parser, args)

    return args, parser


def main():
    """
    Main CLI function for raiseorlaunch.
    """
    args, parser = parse_arguments()

    logger.debug('Provided arguments: {}'.format(args))

    try:
        rol = Raiseorlaunch(command=args.command,
                            wm_class=args.wm_class,
                            wm_instance=args.wm_instance,
                            wm_title=args.wm_title,
                            scratch=args.scratch,
                            con_mark=args.con_mark,
                            workspace=args.workspace,
                            ignore_case=args.ignore_case,
                            event_time_limit=args.event_time_limit)
    except RaiseorlaunchError as e:
        parser.error(str(e))

    rol.run()


if __name__ == '__main__':
    main()
