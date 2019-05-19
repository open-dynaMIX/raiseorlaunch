import os
import sys
from collections import namedtuple

import i3ipc
import pytest

from raiseorlaunch import Raiseorlaunch, raiseorlaunch
from tests.tree import tree


@pytest.fixture()
def default_args():
    return {
        "wm_class": None,
        "wm_instance": None,
        "wm_title": None,
        "command": None,
        "workspace": None,
        "target_workspace": None,
        "scratch": False,
        "con_mark": None,
        "event_time_limit": 2.0,
        "ignore_case": False,
        "cycle": False,
        "leave_fullscreen": False,
    }


@pytest.fixture()
def default_args_cli(default_args):
    default_args["debug"] = False
    return default_args


@pytest.fixture()
def minimal_args(default_args):
    default_args["wm_class"] = "some_class"
    return default_args


@pytest.fixture
def Workspace():
    return namedtuple("Workspace", ("name"))


@pytest.fixture()
def Con(Workspace):
    class CreateCon:
        def __init__(
            self,
            window_class="some_class",
            window_instance="some_instance",
            name="some_name",
            id="some_id",
            workspace_name="some_workspace",
            focused=False,
        ):
            self.window_class = window_class
            self.window_instance = window_instance
            self.name = name
            self.id = id
            self.workspace_name = workspace_name
            self.focused = focused
            self.calls = []

        def workspace(self):
            return Workspace(name=self.workspace_name)

        def command(self, *args, **kwargs):
            self.calls += [args, kwargs]

    return CreateCon


@pytest.fixture()
def sys_argv_handler():
    old_sys_argv = sys.argv
    yield
    sys.argv = old_sys_argv


@pytest.fixture
def tree_mock():
    return i3ipc.Con(tree, None, None)


@pytest.fixture
def run_command_mock(mocker):
    return mocker.patch.object(raiseorlaunch.i3ipc.Connection, "command")


@pytest.fixture
def i3ipc_mock(mocker, tree_mock):
    os.environ["I3SOCK"] = "/dev/null"
    mocker.patch.object(
        raiseorlaunch.i3ipc.Connection, "get_tree", return_value=tree_mock
    )
    mocker.patch.object(i3ipc.socket.socket, "connect")


@pytest.fixture
def rol(minimal_args, i3ipc_mock):
    rol = Raiseorlaunch(**minimal_args)
    return rol
