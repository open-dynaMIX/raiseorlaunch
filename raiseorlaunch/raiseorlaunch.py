# -*- coding: utf-8 -*-

"""
This is the module for raiseorlaunch. A run-or-raise-application-launcher
for i3 window manager.
"""


from __future__ import print_function, unicode_literals


__title__ = 'raiseorlaunch'
__description__ = 'A run-or-raise-application-launcher for i3 window manager.'
__version__ = '1.0.1'
__license__ = 'MIT'
__author__ = 'Fabio Rämi'


import sys
import abc
from datetime import datetime
import re
import logging
try:
    import i3ipc
except ImportError:
    print("\033[31;1mError: Module i3ipc not found.\033[0m", file=sys.stderr)
    sys.exit(1)


logger = logging.getLogger(__name__)
# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta(str('ABC'), (object,), {'__slots__': ()})


class RolBase(ABC):
    """

    Base class for raiseorlaunch.

    Args:
        command (str): The command to execute, if no matching window was found.
        wm_class (str, optional): Regex for the the window class.
        wm_instance (str, optional): Regex for the the window instance.
        wm_title (str, optional): Regex for the the window title.
        ignore_case (bool, optional): Ignore case when comparing
                                      window-properties with provided
                                      arguments.
        no_startup_id (bool, optional): use --no-startup-id when running
                                        command with exec.

    """

    def __init__(self,
                 command,
                 wm_class='',
                 wm_instance='',
                 wm_title='',
                 ignore_case=False,
                 no_startup_id=False):
        self.command = command
        self.wm_class = wm_class
        self.wm_instance = wm_instance
        self.wm_title = wm_title
        self.ignore_case = ignore_case
        self.no_startup_id = no_startup_id

        self.i3 = i3ipc.Connection()

        self.windows = []
        self.regex_flags = []

        if self.ignore_case:
            self.regex_flags.append(re.IGNORECASE)

        self._check_args()

    @abc.abstractmethod
    def run(self):
        """
        Search for running window that matches provided properties
        and act accordingly.
        """
        pass

    def _check_args(self):
        """
        Verify that window properties are provided.
        """
        if not self.wm_class and not self.wm_instance and not self.wm_title:
            raise TypeError('You need to specify '
                            '"wm_class", "wm_instance" or "wm_title.')

    def _run_command(self):
        """
        Run the specified command with exec.
        """
        if self.no_startup_id:
            self.command = 'exec --no-startup-id "{}"'.format(self.command)
        else:
            self.command = 'exec "{}"'.format(self.command)
        logger.debug('Executing command: {}'.format(self.command))
        self.i3.command(self.command)

    def _get_window_list(self):
        """
        Get the list of windows.

        Returns:
            list: Instances of Con()
        """
        logger.debug('Getting list of windows.')
        return self.i3.get_tree().leaves()

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
        return self.i3.get_tree().find_focused().workspace()

    def match_regex(self, regex, string_to_match):
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
        if re.match(*matchlist):
            return True
        else:
            False

    def _log_format_con(self, window):
        return '<Con: class="{}" instance="{}" title="{}" id={}>'.format(
            window.window_class, window.window_instance, window.name,
            window.id)

    def _compare_running(self, window):
        """
        Compare the properties of a running window with the ones provided.

        Args:
            window: Con object.

        Returns:
            bool: True for match, False otherwise.
        """
        for (pattern, value) in [(self.wm_class, window.window_class),
                                 (self.wm_instance, window.window_instance),
                                 (self.wm_title, window.name)]:
            if pattern:
                if not self.match_regex(pattern, value):
                    return False

        logger.debug('Window match: {}'.format(self._log_format_con(window)))
        return True

    def is_running(self, window_list):
        """
        Compare windows in list with provided properties.

        Args:
            window_list: Instances of Con()

        Returns:
            Con() instance if found, None otherwise.
        """
        found = []
        for leave in window_list:
            if self._compare_running(leave):
                found.append(leave)

        if len(found) > 1:
            logger.warning('Found multiple windows that match the properties. '
                           'Using one at random.')
        elif len(found) < 1:
            return None

        return found[0]

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
            win_id (int): window id

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug('Showing scratch window: {}'.format(
            self._log_format_con(window)))
        window.command('scratchpad show')

    def switch_workspace(self, workspace):
        """
        Focus another workspace.

        Args:
            workspace (str): workspace

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug('Switching to workspace: {}'.format(workspace.name))
        return self.i3.command(
            'workspace {}'.format(workspace.name)
            )[0]['success']

    def _handle_running(self, running, current_ws):
        """
        Handle app is running and not explicitly using scratchpad.

        Args:
            running (dict): {'id': int, 'scratch': bool, 'focused': bool}
            current_ws (str): currently used workspace.
        """
        if not running.focused:
            self.focus_window(running)
            running.command('focus')
        else:
            if current_ws.name == self.get_current_workspace().name:
                logger.debug('We\'re on the right workspace. '
                             'Switching anyway to retain '
                             'workspace_back_and_forth '
                             'functionality.')
                self.switch_workspace(current_ws)


class Raiseorlaunch(RolBase):
    """

    Run or raise an application in i3 window manager.

    Additional args:
        scratch (bool, optional): Indicate if the scratchpad should be used.

    """

    def __init__(self, *args, **kwargs):
        if 'scratch' in kwargs:
            self.scratch = kwargs['scratch']
            kwargs.pop('scratch')
        else:
            self.scratch = False

        self.timestamp = None
        self.timelimit = 7

        super(Raiseorlaunch, self).__init__(*args, **kwargs)

    def is_running(self, window_list):
        """
        Compare windows in list with provided properties.

        Args:
            window_list: Instances of Con()

        Returns:
            Con() instance if found, None otherwise.
        """
        found = []
        for leave in window_list:
            if self.scratch and not leave.parent.scratchpad_state == 'changed':
                continue
            if self._compare_running(leave):
                found.append(leave)

        if len(found) > 1:
            logger.warning('Found multiple windows that match the properties. '
                           'Using the first found.')
        elif len(found) < 1:
            return None

        return found[0]

    def _handle_running_scratch(self, running, current_ws):
        """
        Handle app is running and explicitly using scratchpad.

        Args:
            running (dict): {'id': int, 'scratch': bool, 'focused': bool}
            current_ws (str): currently used workspace.
        """
        if not running.focused:
            if current_ws.name == running.workspace().name:
                self.focus_window(running)
            else:
                self.show_scratch(running)
        else:
            self.show_scratch(running)

    def _handle_not_running(self):
        if self.scratch:
            self.i3.on("window::new", self._callback_new_window)
            self._run_command()
            self.timestamp = datetime.now()
            self.i3.main()
        else:
            self._run_command()

    def _callback_new_window(self, c, e):
        logger.debug('WindowEvent callback: {}'
                     .format(self._log_format_con(e.container)))

        timediff = datetime.now() - self.timestamp
        if timediff.seconds > self.timelimit:
            exit(0)

        if self._compare_running(e.container):
            if self.scratch:
                self.move_scratch(e.container)
                self.show_scratch(e.container)

    def run(self):
        """
        Search for running window that matches provided properties
        and act accordingly.
        """
        window_list = self._get_window_list()
        if window_list:
            running = self.is_running(window_list)
            current_ws = self.get_current_workspace()
            if running:
                logger.debug('Application is running on workspace "{}": {}'
                             .format(current_ws.name,
                                     self._log_format_con(running)))
                if running.parent.scratchpad_state == 'changed':
                    self._handle_running_scratch(running, current_ws)
                else:
                    self._handle_running(running, current_ws)
            else:
                logger.debug('Application is not running.')
                self._handle_not_running()
        else:
            logger.debug('Application is not running.')
            self._handle_not_running()


class RaiseorlaunchWorkspace(RolBase):
    """

    Run or raise an application on a specific workspace in i3 window manager.

    Additional args:
        workspace (str): The workspace that should be used for the application.

    """

    def __init__(self, *args, **kwargs):
        if 'workspace' in kwargs:
            self.workspace = kwargs['workspace']
            kwargs.pop('workspace')
        else:
            raise TypeError("__init__() missing 1 required positional "
                            "argument: 'workspace'")
        super(RaiseorlaunchWorkspace, self).__init__(*args, **kwargs)

    def _get_window_list(self):
        """
        Get the list of windows on given workspace.

        Returns:
            list: Instances of Con() if workspace is found else None
        """
        logger.debug('Getting list of windows on workspace: {}.'
                     .format(self.workspace))
        workspaces = self.i3.get_tree().workspaces()
        for workspace in workspaces:
            if workspace.name == self.workspace:
                return workspace.leaves()

    def _handle_not_running(self, current_ws):
        logger.debug('Application is not running.')
        if not current_ws.name == self.workspace:
            self.i3.command('workspace {}'.format(self.workspace))
        self._run_command()

    def run(self):
        """
        Search for running window that matches provided properties
        and act accordingly.
        """
        window_list = self._get_window_list()
        current_ws = self.get_current_workspace()
        if window_list:
            running = self.is_running(window_list)
            if running:
                logger.debug('Application is running on workspace "{}": {}'
                             .format(current_ws.name,
                                     self._log_format_con(running)))
                self._handle_running(running, current_ws)
            else:
                self._handle_not_running(current_ws)
        else:
            self._handle_not_running(current_ws)
