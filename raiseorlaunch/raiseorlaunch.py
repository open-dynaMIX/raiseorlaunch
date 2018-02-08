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


class RaiseorlaunchError(Exception):
    pass


class Raiseorlaunch(object):
    """
    Main class for raiseorlaunch.

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
        event_time_limit (int or float, optional): Time limit in seconds to
                                                   listen to window events
                                                   when using the scratchpad.
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
                 event_time_limit=2):
        self.command = command
        self.wm_class = wm_class
        self.wm_instance = wm_instance
        self.wm_title = wm_title
        self.workspace = workspace
        self.scratch = scratch
        self.con_mark = con_mark
        self.ignore_case = ignore_case
        self.event_time_limit = event_time_limit if event_time_limit else 2

        self.regex_flags = []
        if self.ignore_case:
            self.regex_flags.append(re.IGNORECASE)

        self._check_args()

        self.i3 = i3ipc.Connection()
        self.tree = self.i3.get_tree()

        self._timestamp = None

    def _check_args(self):
        """
        Verify that...
         - ...window properties are provided.
         - ...there is no workspace provided when using the scratchpad
        """
        if not self.wm_class and not self.wm_instance and not self.wm_title:
            raise RaiseorlaunchError('You need to specify '
                                     '"wm_class", "wm_instance" or "wm_title.')
        if self.workspace and self.scratch:
            raise RaiseorlaunchError('You cannot use the scratchpad on a '
                                     'specific workspace.')

    def _log_format_con(self, window):
        """
        Create an informatinal string for logging leaves.

        Returns:
            str: '<Con: class="{}" instance="{}" title="{}" id={}>'
        """
        return '<Con: class="{}" instance="{}" title="{}" id={}>'.format(
            window.window_class, window.window_instance, window.name,
            window.id)

    def _match_regex(self, regex, string_to_match):
        """
        Match a regex with provided flags.

        Args:
            regex: The regex to use
            string_to_match: The string we should match

        Returns:
            bool: True for match, False otherwise.
        """
        matchlist = [regex, string_to_match, *self.regex_flags]
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
                        l.parent.scratchpad_state in ['changed', 'fresh']]
            else:
                return leaves
        else:
            logger.debug('Getting list of windows on workspace: {}.'
                         .format(self.workspace))
            workspaces = self.tree.workspaces()
            for workspace in workspaces:
                if workspace.name == self.workspace:
                    return workspace.leaves()
            return []

    def _find_marked_window(self):
        """
        Find window with given mark. Restrict to given workspace
        if self.workspace is set.

        Returns:
            list: Containing one instance of Con() if found, None otherwise
        """
        found = self.tree.find_marked(self.con_mark)
        if found and self.workspace:
            if not found[0].workspace().name == self.workspace:
                found = None
        return found

    def _is_running(self):
        """
        Compare windows in list with provided properties.

        Args:
            window_list: Instances of Con().

        Returns:
            Con() instance if found, None otherwise.
        """
        if self.con_mark:
            found = self._find_marked_window()
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

    def run_command(self):
        """
        Run the specified command with exec.
        """
        command = 'exec {}'.format(self.command)
        logger.debug('Executing command: {}'.format(command))
        self.i3.command(command)

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
            obj: The workspace Con()
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
        logger.debug('Enabling floating mode on newly created window: {}'
                     .format(self._log_format_con(window)))
        # Somehow this is needed to retain window geometry
        # (e.g. when using xterm -geometry)
        window.command('floating enable')
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
        self.i3.command('workspace {}'.format(name))

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
            self._timestamp = datetime.now()
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
        window = event.container
        logger.debug('Event callback: {}'
                     .format(self._log_format_con(window)))

        timediff = datetime.now() - self._timestamp
        if timediff > timedelta(seconds=self.event_time_limit):
            logger.debug('Time limit exceeded. Exiting.')
            exit(0)

        if self._compare_running(window):
            if self.scratch:
                self.move_scratch(window)
                self.show_scratch(window)
            if self.con_mark:
                self.set_con_mark(window)

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
            if self.scratch:
                self._handle_running_scratch(running, current_ws)
            else:
                self._handle_running(running, current_ws)
        else:
            logger.debug('Application is not running.')
            self._handle_not_running()
