# -*- coding: utf-8 -*-

"""
This is the module for raiseorlaunch. A run-or-raise-application-launcher
for i3 window manager.
"""


__title__ = "raiseorlaunch"
__description__ = "A run-or-raise-application-launcher for i3 window manager."
__version__ = "2.3.3"
__license__ = "MIT"
__author__ = "Fabio Rämi"


import logging
import re
import sys

try:
    import i3ipc
except ImportError:  # pragma: no cover
    print("\033[31;1mError: Module i3ipc not found.\033[0m", file=sys.stderr)
    sys.exit(1)


logger = logging.getLogger(__name__)


def check_positive(value):
    try:
        fvalue = float(value)
    except ValueError:
        return False
    else:
        if fvalue <= 0:
            return False
        return fvalue


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
        workspace (str, optional): The workspace that should be used for the application.
        target_workspace (str, optional): The workspace that should be used for the
                                application.
        scratch (bool, optional): Use the scratchpad.
        ignore_case (bool, optional): Ignore case when comparing
                                      window-properties with provided
                                      arguments.
        event_time_limit (int or float, optional): Time limit in seconds to
                                                   listen to window events
                                                   when using the scratchpad.
        cycle (bool, optional): Cycle through matching windows.
        leave_fullscreen (bool, optional): Leave fullscreen on target
                                           workspace.
    """

    def __init__(
        self,
        command,
        wm_class=None,
        wm_instance=None,
        wm_title=None,
        workspace=None,
        target_workspace=None,
        scratch=False,
        con_mark=None,
        ignore_case=False,
        event_time_limit=2,
        cycle=False,
        leave_fullscreen=False,
    ):
        self.command = command
        self.wm_class = wm_class
        self.wm_instance = wm_instance
        self.wm_title = wm_title
        self.workspace = workspace
        self.target_workspace = target_workspace or workspace
        self.scratch = scratch
        self.con_mark = con_mark
        self.ignore_case = ignore_case
        self.event_time_limit = event_time_limit
        self.cycle = cycle
        self.leave_fullscreen = leave_fullscreen

        self.regex_flags = [re.IGNORECASE] if self.ignore_case else []

        self._check_args()

        self.i3 = i3ipc.Connection()
        self.tree = self.i3.get_tree()
        self.current_ws = self.get_current_workspace()

    def _check_args(self):
        """
        Verify that...
         - ...window properties are provided.
         - ...there is no workspace provided when using the scratchpad
         - ...event_time_limit, if provided, is a positive int or float
         - ...workspace and init_workspace are not set to something different
        """
        if not self.wm_class and not self.wm_instance and not self.wm_title:
            raise RaiseorlaunchError(
                "You need to specify " '"wm_class", "wm_instance" or "wm_title.'
            )
        if (self.workspace or self.target_workspace) and self.scratch:
            raise RaiseorlaunchError(
                "You cannot use the scratchpad on a specific workspace."
            )
        if not check_positive(self.event_time_limit):
            raise RaiseorlaunchError(
                "The event time limit must be a positive integer or float!"
            )
        if self.workspace and self.target_workspace:
            if not self.workspace == self.target_workspace:
                raise RaiseorlaunchError(
                    "Setting workspace and initial workspace is ambiguous!"
                )

    def _need_to_listen_to_events(self):
        """
        Evaluate if we need to listen to window events.

        :return: bool
        """
        return any([self.scratch, self.con_mark, self.target_workspace])

    @staticmethod
    def _log_format_con(window):
        """
        Create an informatinal string for logging leaves.

        Returns:
            str: '<Con: class="{}" instance="{}" title="{}" id={}>'
        """

        def quote(value):
            if isinstance(value, str):
                return '"{}"'.format(value)
            return value

        return "<Con: class={} instance={} title={} id={}>".format(
            quote(window.window_class),
            quote(window.window_instance),
            quote(window.name),
            window.id,
        )

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
        for (pattern, value) in [
            (self.wm_class, window.window_class),
            (self.wm_instance, window.window_instance),
            (self.wm_title, window.name),
        ]:

            if pattern and (not value or not self._match_regex(pattern, value)):
                return False

        logger.debug("Window match: {}".format(self._log_format_con(window)))
        return True

    def _get_window_list(self):
        """
        Get the list of windows.

        Returns:
            list: Instances of Con()
        """
        if not self.workspace:
            logger.debug("Getting list of windows.")
            leaves = self.tree.leaves()
            if self.scratch:
                return [
                    leave
                    for leave in leaves
                    if leave.parent.scratchpad_state in ["changed", "fresh"]
                ]
            else:
                return leaves
        else:
            logger.debug(
                "Getting list of windows on workspace: {}.".format(self.workspace)
            )
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

        Returns:
            List of Con() instances if found, None otherwise.
        """
        if self.con_mark:
            return self._find_marked_window()

        window_list = self._get_window_list()
        found = []
        for leave in window_list:
            if (
                leave.window_class
                == leave.window_instance
                == leave.window_title
                is None
            ):
                logger.debug("Window without any properties found.")
                continue
            if self._compare_running(leave):
                found.append(leave)

        if len(found) > 1:  # pragma: no cover
            logger.debug("Multiple windows match the properties.")

        return found if found else None

    def run_command(self):
        """
        Run the specified command with exec.
        """
        command = "exec {}".format(self.command)
        logger.debug("Executing command: {}".format(command))
        self.i3.command(command)

    def set_con_mark(self, window):
        """
        Set con_mark on window.

        Args:
            window: Instance of Con()
        """
        logger.debug(
            'Setting con_mark "{}" on window: {}'.format(
                self.con_mark, self._log_format_con(window)
            )
        )
        window.command("mark {}".format(self.con_mark))

    def focus_window(self, window):
        """
        Focus window.

        Args:
            window: Instance of Con()
        """
        logger.debug("Focusing window: {}".format(self._log_format_con(window)))
        window.command("focus")

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
        """
        logger.debug(
            "Enabling floating mode on newly created window: {}".format(
                self._log_format_con(window)
            )
        )
        # Somehow this is needed to retain window geometry
        # (e.g. when using xterm -geometry)
        window.command("floating enable")
        logger.debug(
            "Moving newly created window to the scratchpad: {}".format(
                self._log_format_con(window)
            )
        )
        window.command("move scratchpad")

    def show_scratch(self, window):
        """
        Show scratchpad window.

        Args:
            window: Instance of Con().
        """
        logger.debug(
            "Toggling visibility of scratch window: {}".format(
                self._log_format_con(window)
            )
        )
        window.command("scratchpad show")

    def switch_to_workspace_by_name(self, name):
        """
        Focus another workspace.

        Args:
            name (str): workspace name
        """
        logger.debug("Switching to workspace: {}".format(name))
        self.i3.command("workspace {}".format(name))

    @staticmethod
    def move_con_to_workspace_by_name(window, workspace):
        """
        Move window to workspace.

        Args:
            window: Instance of Con().
            workspace: str
        """
        logger.debug("Moving window to workspace: {}".format(workspace))
        window.command("move container to workspace {}".format(workspace))

    def leave_fullscreen_on_workspace(self, workspace_name, exceptions=None):
        """
        Make sure no application is in fullscreen mode on provided workspace.

        Args:
            workspace_name: str
            exceptions: list of Con()

        Returns:
            None
        """
        exceptions = exceptions if exceptions else []
        cons_on_ws = self.tree.find_named("^{}$".format(workspace_name))
        cons = cons_on_ws[0].find_fullscreen() if cons_on_ws else []
        for con in cons:
            if con.type == "workspace" or con in exceptions:
                continue
            logger.debug(
                "Leaving fullscreen for con: {}".format(self._log_format_con(con))
            )
            con.command("fullscreen")

    def _choose_if_multiple(self, running):
        """
        If multiple windows are found, determine which one to raise.

        If init_workspace is set, prefer a window on that workspace,
        otherwise use the first in the tree.

        Args:
            running: list of Con()

        Returns:
            Instance of Con().
        """
        if len(running) == 1:
            return running[0]

        window = running[0]
        if self.target_workspace:
            multi_msg = (
                "Found multiple windows that match the "
                "properties. Using the first in the tree, "
                "preferably on target workspace."
            )
            for w in running:
                if w.workspace().name == self.target_workspace:
                    window = w
                    break
        else:
            multi_msg = (
                "Found multiple windows that match the "
                "properties. Using the first in the tree."
            )

        logger.debug(multi_msg)
        return window

    def _handle_running(self, running):
        """
        Handle app is running one or multiple times.

        Args:
            running: List of Con() instances.
        """
        # there is no need to do anything if self.leave_fullscreen is True,
        # because focussing the window will take care of that.

        if self.cycle and len(running) > 1:
            for w in running:
                if w.focused:
                    self._handle_running_cycle(running)
                    return

        window = self._choose_if_multiple(running)

        logger.debug(
            'Application is running on workspace "{}": {}'.format(
                window.workspace().name, self._log_format_con(window)
            )
        )
        if self.scratch:
            self._handle_running_scratch(window)
        else:
            self._handle_running_no_scratch(window)

    def _handle_running_no_scratch(self, window):
        """
        Handle app is running and not explicitly using scratchpad.

        Args:
            window: Instance of Con().
        """
        if not window.focused:
            self.focus_window(window)
        else:
            if self.current_ws.name == self.get_current_workspace().name:
                logger.debug(
                    "We're on the right workspace. "
                    "Switching anyway to retain "
                    "workspace_back_and_forth "
                    "functionality."
                )
                self.switch_to_workspace_by_name(self.current_ws.name)

    def _handle_running_scratch(self, window):
        """
        Handle app is running and explicitly using scratchpad.

        Args:
            window: Instance of Con().
        """
        if not window.focused:
            if self.current_ws.name == window.workspace().name:
                self.focus_window(window)
            else:
                self.show_scratch(window)
        else:
            self.show_scratch(window)

    def _handle_running_cycle(self, windows):
        """
        Handle cycling through running apps.

        Args:
            windows: List with instances of Con().
        """
        logger.debug("Cycling through matching windows.")
        switch = False
        w = None
        windows.append(windows[0])
        for window in windows:  # pragma: no branch
            if switch:
                w = window
                break
            if window.focused:
                switch = True

        if w:
            logger.debug(
                'Application is running on workspace "{}": {}'.format(
                    w.workspace().name, self._log_format_con(w)
                )
            )

            self.focus_window(w)
        else:  # pragma: no cover
            logger.error("No running windows received. This should not happen!")

    def _handle_not_running(self):
        """
        Handle app is not running.
        """
        if self.target_workspace:
            if not self.current_ws.name == self.target_workspace:
                self.switch_to_workspace_by_name(self.target_workspace)

        if self.leave_fullscreen:
            self.leave_fullscreen_on_workspace(
                self.target_workspace or self.current_ws.name
            )

        if self._need_to_listen_to_events():
            self.i3.on("window::new", self._callback_new_window)
        self.run_command()

        if self._need_to_listen_to_events():
            self.i3.main(timeout=self.event_time_limit)

    def _callback_new_window(self, connection, event):
        """
        Callback function for window::new events.

        This handles moving new windows to the desired workspace or
        the scratchpad and setting con_marks.
        """
        window = event.container
        logger.debug("Event callback: {}".format(self._log_format_con(window)))

        if self._compare_running(window):
            if self.scratch:
                self.move_scratch(window)
                self.show_scratch(window)
            if self.con_mark:
                self.set_con_mark(window)

            if self.target_workspace:
                # This is necessary, because window.workspace() returns None
                w = connection.get_tree().find_by_id(window.id)

                if not w.workspace().name == self.target_workspace:
                    self.move_con_to_workspace_by_name(w, self.target_workspace)

    def run(self):
        """
        Search for running window that matches provided properties
        and act accordingly.
        """
        running = self._is_running()
        if running:
            self._handle_running(running)
        else:
            logger.debug("Application is not running.")
            self._handle_not_running()
