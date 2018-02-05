# -*- coding: utf-8 -*-

"""
This is the module for raiseorlaunch. A run-or-raise-application-launcher
for i3 window manager.
"""


__title__ = 'raiseorlaunch'
__description__ = 'A run-or-raise-application-launcher for i3 window manager.'
__version__ = '2.0.0'
__license__ = 'MIT'
__author__ = 'Fabio Rämi'


import sys
from datetime import datetime, timedelta
import re
import logging
try:
    import i3ipc
except ImportError:
    print("\033[31;1mError: Module i3ipc not found.\033[0m", file=sys.stderr)
    sys.exit(1)


logger = logging.getLogger(__name__)


class Raiseorlaunch(object):
    """

    Base class for raiseorlaunch.

    Args:
        command (str): The command to execute, if no matching window was found.
        wm_class (str, optional): Regex for the the window class.
        wm_instance (str, optional): Regex for the the window instance.
        wm_title (str, optional): Regex for the the window title.
        workspace (str): The workspace that should be used for the application.
        scratch (bool, optional): Indicate if the scratchpad should be used.
        ignore_case (bool, optional): Ignore case when comparing
                                      window-properties with provided
                                      arguments.
        no_startup_id (bool, optional): use --no-startup-id when running
                                        command with exec.
        event_time_limit (integer, optional): Time limit in seconds to listen
                                              to window events when using the
                                              scratchpad.

    """

    def __init__(self,
                 command,
                 wm_class=None,
                 wm_instance=None,
                 wm_title=None,
                 workspace=None,
                 scratch=False,
                 con_mark=None,
                 ignore_case=False,
                 no_startup_id=False,
                 event_time_limit=2):
        self.command = command
        self.wm_class = wm_class
        self.wm_instance = wm_instance
        self.wm_title = wm_title
        self.workspace = workspace
        self.scratch = scratch
        self.con_mark = con_mark
        self.ignore_case = ignore_case
        self.no_startup_id = no_startup_id
        self.event_time_limit = event_time_limit if event_time_limit else 2

        self.timestamp = None
        self.windows = []
        self.regex_flags = []

        if self.ignore_case:
            self.regex_flags.append(re.IGNORECASE)

        if self.scratch:
            self._handle_running_method = self._handle_running_scratch
        else:
            self._handle_running_method = self._handle_running

        self._check_args()

        self.i3 = i3ipc.Connection()
        self.tree = self.i3.get_tree()

    def _check_args(self):
        """
        Verify that window properties are provided.
        """
        if not self.wm_class and not self.wm_instance and not self.wm_title:
            raise TypeError('You need to specify '
                            '"wm_class", "wm_instance" or "wm_title.')
        if self.workspace and self.scratch:
            raise TypeError('You cannot use the scratchpad on a specific '
                            'workspace.')

    def _log_format_con(self, window):
        """
        Create an informatinal string for logging leaves.

        Returns:
            str: '<Con: class="{}" instance="{}" title="{}" id={}>'
        """
        return '<Con: class="{}" instance="{}" title="{}" id={}>'.format(
            window.window_class, window.window_instance, window.name,
            window.id)

    def _get_window_list(self):
        """
        Get the list of windows.

        Returns:
            list: Instances of Con()
        """
        if not self.workspace:
            logger.debug('Getting list of windows.')
            leaves = self.tree.leaves()
            if self.scratch:
                return [l for l in leaves if
                        l.parent.scratchpad_state == 'changed']
            else:
                return leaves
        else:
            logger.debug('Getting list of windows on workspace: {}.'
                         .format(self.workspace))
            workspaces = self.tree.workspaces()
            for workspace in workspaces:
                if workspace.name == self.workspace:
                    return workspace.leaves()

    def _match_regex(self, regex, string_to_match):
        """
        Match a regex with provided flags.

        Args:
            regex: The regex to use
            string_to_match: The string we should match

        Returns:
            bool: True for match, False otherwise.
        """
        matchlist = [regex, string_to_match]
        matchlist.extend(self.regex_flags)
        return True if re.match(*matchlist) else False

    def _compare_running(self, window):
        """
        Compare the properties of a running window with the ones provided.

        Args:
            window: Instance of Con().

        Returns:
            bool: True for match, False otherwise.
        """
        for (pattern, value) in [(self.wm_class, window.window_class),
                                 (self.wm_instance, window.window_instance),
                                 (self.wm_title, window.name)]:
            if pattern:
                if not self._match_regex(pattern, value):
                    return False

        logger.debug('Window match: {}'.format(self._log_format_con(window)))
        return True

    def _is_running(self):
        """
        Compare windows in list with provided properties.

        Args:
            window_list: Instances of Con().

        Returns:
            Con() instance if found, None otherwise.
        """
        if self.con_mark:
            found = self.tree.find_marked(self.con_mark)
        else:
            window_list = self._get_window_list()
            found = []
            for leave in window_list:
                if self._compare_running(leave):
                    found.append(leave)

            if len(found) > 1:
                logger.warning('Found multiple windows that match the '
                               'properties. Using one at random.')

        return found[0] if found else None

    def _handle_running(self, window, current_ws):
        """
        Handle app is running and not explicitly using scratchpad.

        Args:
            window: Instance of Con().
            current_ws: Instance of Con().
        """
        if not window.focused:
            self.focus_window(window)
        else:
            if current_ws.name == self.get_current_workspace().name:
                logger.debug('We\'re on the right workspace. '
                             'Switching anyway to retain '
                             'workspace_back_and_forth '
                             'functionality.')
                self.switch_to_workspace_by_name(current_ws.name)

    def _handle_running_scratch(self, window, current_ws):
        """
        Handle app is running and explicitly using scratchpad.

        Args:
            window: Instance of Con().
            current_ws: Instance of Con().
        """
        if not window.focused:
            if current_ws.name == window.workspace().name:
                self.focus_window(window)
            else:
                self.show_scratch(window)
        else:
            self.show_scratch(window)

    def _handle_not_running(self):
        """
        Handle app is not running.
        """
        if self.scratch or self.con_mark:
            self.i3.on("window::new", self._callback_new_window)
            self.run_command()
            self.timestamp = datetime.now()
            self.i3.main()
        else:
            if self.workspace:
                current_ws = self.get_current_workspace()
                if not current_ws.name == self.workspace:
                    self.switch_to_workspace_by_name(self.workspace)
            self.run_command()

    def _callback_new_window(self, connection, event):
        """
        Callback function for window::new events.

        This handles moving new windows to the scratchpad
        and setting con_marks.
        """
        logger.debug('WindowEvent callback: {}'
                     .format(self._log_format_con(event.container)))

        timediff = datetime.now() - self.timestamp
        if timediff > timedelta(seconds=self.event_time_limit):
            logger.debug('Time limit exceeded. Exiting.')
            exit(0)

        if self._compare_running(event.container):
            if self.scratch:
                self.move_scratch(event.container)
                self.show_scratch(event.container)
            if self.con_mark:
                self.set_con_mark(event.container)

    def set_con_mark(self, window):
        """
        Set con_mark on window.

        Args:
            window: Instance of Con()
        """
        logger.debug('Setting con_mark "{}" on window: {}'
                     .format(self.con_mark,
                             self._log_format_con(window)))
        window.command('mark {}'.format(self.con_mark))

    def run_command(self):
        """
        Run the specified command with exec.
        """
        if self.no_startup_id:
            self.command = 'exec --no-startup-id {}'.format(self.command)
        else:
            self.command = 'exec {}'.format(self.command)
        logger.debug('Executing command: {}'.format(self.command))
        self.i3.command(self.command)

    def focus_window(self, window):
        """
        Focus window.

        Args:
            window: Instance of Con()
        """
        logger.debug('Focusing window: {}'.format(
            self._log_format_con(window)))
        window.command('focus')

    def get_current_workspace(self):
        """
        Get the current workspace name.

        Returns:
            obj: The workspace Con
        """
        return self.tree.find_focused().workspace()

    def move_scratch(self, window):
        """
        Move window to scratchpad.

        Args:
            window: Instance of Con().

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug('Moving newly created window to the scratchpad: {}'
                     .format(self._log_format_con(window)))
        window.command('move scratchpad')

    def show_scratch(self, window):
        """
        Show scratchpad window.

        Args:
            window: Instance of Con().

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug('Toggling visibility of scratch window: {}'.format(
            self._log_format_con(window)))
        window.command('scratchpad show')

    def switch_to_workspace_by_name(self, name):
        """
        Focus another workspace.

        Args:
            name (str): workspace name

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug('Switching to workspace: {}'.format(name))
        return self.i3.command(
            'workspace {}'.format(name)
            )[0]['success']

    def run(self):
        """
        Search for running window that matches provided properties
        and act accordingly.
        """
        running = self._is_running()
        if running:
            current_ws = self.get_current_workspace()
            logger.debug('Application is running on workspace "{}": {}'
                         .format(current_ws.name,
                                 self._log_format_con(running)))
            self._handle_running_method(running, current_ws)
        else:
            logger.debug('Application is not running.')
            self._handle_not_running()
