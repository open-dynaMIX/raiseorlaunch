import re

import i3ipc
import pytest

from raiseorlaunch import (
    Raiseorlaunch,
    RaiseorlaunchError,
    check_positive,
    raiseorlaunch,
)


def test_init_success(default_args, mocker):
    mocker.patch.object(i3ipc, "Connection")
    default_args.update({"wm_class": "some_class"})
    assert Raiseorlaunch(**default_args)


@pytest.mark.parametrize(
    "args,error_string",
    [
        ({}, 'You need to specify "wm_class", "wm_instance" or "wm_title.'),
        (
            {"workspace": "ws", "scratch": True, "wm_class": "some_class"},
            "You cannot use the scratchpad on a specific workspace.",
        ),
        (
            {"event_time_limit": "string", "wm_class": "some_class"},
            "The event time limit must be a positive integer or float!",
        ),
        (
            {
                "workspace": "ws",
                "target_workspace": "other_ws",
                "wm_class": "some_class",
            },
            "Setting workspace and initial workspace is ambiguous!",
        ),
        ({"workspace": "ws", "target_workspace": "ws", "wm_class": "some_class"}, None),
    ],
)
def test__check_args(args, error_string, default_args, mocker):
    default_args.update(args)
    mocker.patch.object(i3ipc, "Connection")

    if not error_string:
        Raiseorlaunch(**default_args)
        return

    with pytest.raises(RaiseorlaunchError) as excinfo:
        Raiseorlaunch(**default_args)
        assert str(excinfo.value) == error_string


@pytest.mark.parametrize(
    "value,result",
    [
        (1, 1.0),
        (1.0, 1.0),
        ("1", 1.0),
        ("1.0", 1.0),
        (0, False),
        (-1, False),
        ("0", False),
        ("-1", False),
        ("not a number", False),
    ],
)
def test_check_positive(value, result):
    assert check_positive(value) == result


def test__log_format_con(minimal_args, Con, mocker):
    mocker.patch.object(i3ipc, "Connection")

    rol = Raiseorlaunch(**minimal_args)
    assert (
        rol._log_format_con(Con(window_class=None))
        == '<Con: class=None instance="some_instance" title="some_name" id=some_id>'
    )


@pytest.mark.parametrize(
    "regex,string,success,ignore_case",
    [
        ("qutebrowser", "Qutebrowser", True, True),
        ("qutebrowser", "qutebrowser", True, False),
        ("qutebrowser", "Qutebrowser", False, False),
        ("^qutebrowser", "something_qutebrowser", False, True),
        ("^qutebrowser$", "qutebrowser_something", False, False),
    ],
)
def test__match_regex(minimal_args, ignore_case, regex, string, success, mocker):
    mocker.patch.object(i3ipc, "Connection")
    minimal_args.update({"ignore_case": ignore_case})
    rol = Raiseorlaunch(**minimal_args)
    assert rol._match_regex(regex, string) is success


@pytest.mark.parametrize(
    "config,con_values,success",
    [
        ({"wm_class": "qutebrowser"}, {"window_class": "qutebrowser"}, True),
        (
            {"wm_class": "qutebrowser", "ignore_case": True},
            {"window_class": "Qutebrowser"},
            True,
        ),
        ({"wm_class": "foo"}, {"window_class": "Qutebrowser"}, False),
        ({"wm_class": "foo"}, {"window_class": None}, False),
    ],
)
def test__compare_running(minimal_args, rol, Con, config, con_values, success):
    rol.__dict__.update(config)
    if "ignore_case" in config:
        rol.regex_flags = [re.IGNORECASE]
    con = Con(**con_values)

    assert rol._compare_running(con) == success


@pytest.mark.parametrize(
    "scratch,workspace,count,names",
    [
        (
            False,
            None,
            5,
            ["Home", None, "i3 - improved tiling wm - qutebrowser", "notes", "htop"],
        ),
        (True, None, 2, ["notes", "htop"]),
        (False, "workspace_1", 2, ["i3 - improved tiling wm - qutebrowser", "htop"]),
        (False, "not a workspace", 0, []),
    ],
)
def test__get_window_list(scratch, workspace, count, names, rol):
    rol.scratch = scratch
    rol.workspace = workspace
    window_list = rol._get_window_list()
    assert len(window_list) == count
    assert [w.name for w in window_list] == names


@pytest.mark.parametrize(
    "mark,workspace,success",
    [
        ("my_mark", None, True),
        ("my_mark", "workspace_1", False),
        ("my_qb_mark", "workspace_1", True),
        ("my_mark", "not a workspace", False),
        ("not a mark", None, False),
    ],
)
def test__find_marked_window(mark, workspace, success, rol):
    rol.con_mark = mark
    rol.workspace = workspace
    marked = rol._find_marked_window()
    assert bool(marked) == success


@pytest.mark.parametrize(
    "mark,workspace,wm_class,wm_instance,wm_title,success",
    [
        (None, None, "qutebrowser", None, None, True),
        (None, None, None, "test-qutebrowser", None, True),
        (None, None, None, None, "i3 - improved tiling wm - qutebrowser", True),
        (None, None, "non_existing_class", None, None, False),
        ("my_mark", None, None, None, None, True),
        ("not a mark", None, None, None, None, False),
    ],
)
def test__is_running(mark, workspace, wm_class, wm_instance, wm_title, success, rol):
    rol.con_mark = mark
    rol.workspace = workspace
    rol.wm_class = wm_class
    rol.wm_instance = wm_instance
    rol.wm_title = wm_title
    running = rol._is_running()
    assert bool(running) == success


def test_run_command(run_command_mock, rol):
    rol.command = "worldpeace.py --now"
    rol.run_command()
    run_command_mock.assert_called_once_with("exec worldpeace.py --now")


@pytest.mark.parametrize(
    "workspace,exceptions,called",
    [
        ("workspace_1", None, True),
        ("workspace_1", ["qutebrowser"], False),
        ("not_a_workspace", None, False),
    ],
)
def test_leave_fullscreen_on_workspace(workspace, exceptions, called, rol, mocker):
    con_command = mocker.patch.object(raiseorlaunch.i3ipc.Con, "command")

    if exceptions:
        exceptions = [c for c in rol._get_window_list() if c.window_class in exceptions]

    rol.leave_fullscreen_on_workspace(workspace, exceptions)

    if called:
        con_command.assert_called_once_with("fullscreen")
    else:
        con_command.assert_not_called()


@pytest.mark.parametrize(
    "target_workspace,multi",
    [
        ("workspace_1", True),
        ("workspace_1", False),
        ("not a workspace", True),
        (None, True),
        (None, False),
    ],
)
def test__choose_if_multiple(target_workspace, multi, rol):
    rol.target_workspace = target_workspace
    cons = [
        c
        for c in rol._get_window_list()
        if c.window_instance and c.window_instance.startswith("test")
    ]
    if not multi:
        cons = [cons[0]]
    con = rol._choose_if_multiple(cons)
    assert con.window_class == "qutebrowser"


@pytest.mark.parametrize(
    "cycle,multi,scratch,unfocus,called_method_name",
    [
        (True, True, False, False, "_handle_running_cycle"),
        (True, True, False, True, "_handle_running_no_scratch"),
        (True, False, True, False, "_handle_running_scratch"),
        (True, False, False, False, "_handle_running_no_scratch"),
    ],
)
def test__handle_running(
    cycle, scratch, multi, unfocus, called_method_name, rol, mocker
):
    mock = mocker.patch.object(raiseorlaunch.Raiseorlaunch, called_method_name)
    rol.cycle = cycle
    rol.scratch = scratch
    running = [
        c
        for c in rol._get_window_list()
        if c.window_instance and c.window_instance.startswith("test")
    ]
    if not multi:
        running = [running[0]]

    if unfocus:
        for con in running:
            con.focused = False

    rol._handle_running(running)

    if not cycle:
        assert mock.called


@pytest.mark.parametrize(
    "focused,current_ws_name,called,called_with,con",
    [
        (True, "workspace_1", True, "workspace workspace_1", False),
        (True, "workspace_2", False, None, False),
        (False, "workspace_2", True, "focus", True),
        (False, "workspace_1", True, "focus", True),
    ],
)
def test__handle_running_no_scratch(
    focused, current_ws_name, called, called_with, con, rol, Con, Workspace, mocker
):
    if con:
        command = mocker.patch.object(Con, "command")
    else:
        command = mocker.patch.object(raiseorlaunch.i3ipc.Connection, "command")

    window = Con(focused=focused)

    rol.workspace = "ws"
    rol.current_ws = Workspace(name=current_ws_name)
    rol._handle_running_no_scratch(window)

    if called:
        command.assert_called_once_with(called_with)
    else:
        assert not command.called


@pytest.mark.parametrize(
    "focused,current_workspace_name,con_workspace_name,called_with",
    [
        (True, "notes", "notes", "scratchpad show"),
        (False, "notes", "notes", "focus"),
        (False, "notes", "not_notes", "scratchpad show"),
    ],
)
def test__handle_running_scratch(
    focused,
    current_workspace_name,
    con_workspace_name,
    called_with,
    rol,
    Con,
    Workspace,
    mocker,
):
    mocker.patch.object(Con, "command")
    rol.scratch = True
    rol.current_ws = Workspace(name=current_workspace_name)
    window = Con(focused=focused, workspace_name=con_workspace_name)

    rol._handle_running_scratch(window)

    window.command.assert_called_once_with(called_with)


@pytest.mark.parametrize(
    "focused,match",
    [([True, False, False], 1), ([False, True, False], 2), ([False, False, True], 0)],
)
def test__handle_running_cycle(focused, match, Con, rol, mocker):
    mock = mocker.patch.object(raiseorlaunch.Raiseorlaunch, "focus_window")
    windows = [
        Con(window_class="test-{0}".format(i), focused=focused[i]) for i in range(3)
    ]

    rol._handle_running_cycle(windows)

    mock.assert_called_once_with(windows[match])


@pytest.mark.parametrize(
    "current_ws,target_ws,should_call_switch_ws,handle_event",
    [
        ("ws1", "ws1", False, True),
        ("ws1", None, False, False),
        ("ws1", "ws2", True, True),
    ],
)
@pytest.mark.parametrize("leave_fullscreen", [True, False])
def test__handle_not_running(
    current_ws,
    target_ws,
    should_call_switch_ws,
    handle_event,
    leave_fullscreen,
    rol,
    Workspace,
    mocker,
):
    switch_to_workspace_by_name = mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "switch_to_workspace_by_name"
    )
    leave_fullscreen_on_workspace = mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "leave_fullscreen_on_workspace"
    )
    on = mocker.patch.object(raiseorlaunch.i3ipc.Connection, "on")
    run_command = mocker.patch.object(raiseorlaunch.Raiseorlaunch, "run_command")
    main = mocker.patch.object(raiseorlaunch.i3ipc.Connection, "main")

    rol.current_ws = Workspace(name=current_ws)
    rol.target_workspace = target_ws

    if leave_fullscreen:
        rol.leave_fullscreen = True

    rol._handle_not_running()

    if should_call_switch_ws:
        switch_to_workspace_by_name.assert_called_once_with(target_ws)
    else:
        assert not switch_to_workspace_by_name.called

    if leave_fullscreen:
        leave_fullscreen_on_workspace.assert_called_once_with(target_ws or current_ws)
    else:
        assert not leave_fullscreen_on_workspace.called

    assert on.called == handle_event
    assert run_command.called
    assert main.called == handle_event


@pytest.mark.parametrize("class1,class2", [("class1", "class2")])
@pytest.mark.parametrize(
    "current_ws,target_ws,should_call_move_to_ws",
    [("ws1", "ws1", False), ("ws1", None, False), ("ws1", "ws2", True)],
)
@pytest.mark.parametrize("compare_running", [True, False])
@pytest.mark.parametrize("scratch", [True, False])
@pytest.mark.parametrize("con_mark", [None, "test_con_mark"])
def test__callback_new_window(
    class1,
    class2,
    current_ws,
    target_ws,
    should_call_move_to_ws,
    compare_running,
    scratch,
    con_mark,
    Con,
    Workspace,
    rol,
    mocker,
):
    con_mock = mocker.patch.object(Con, "command")
    con1 = Con(workspace_name="ws1")
    event = mocker.patch.object(raiseorlaunch.i3ipc, "Event")
    event.container = con1
    connection = mocker.patch.object(raiseorlaunch.i3ipc, "Connection")
    connection.get_tree.return_value.find_by_id.return_value = con1
    mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "_compare_running", return_value=compare_running
    )

    rol.scratch = scratch
    rol.con_mark = con_mark
    rol.current_ws = Workspace(name=current_ws)
    rol.target_workspace = target_ws

    rol._callback_new_window(connection, event)

    if not compare_running:
        assert con1.calls == []
        return

    called = []
    not_called = []

    if scratch:
        called += ["floating enable", "move scratchpad", "scratchpad show"]
    else:
        not_called += ["floating enable", "move scratchpad", "scratchpad show"]

    if con_mark:
        called.append("mark {}".format(con_mark))
    else:
        not_called.append("mark {}".format(con_mark))

    if should_call_move_to_ws:
        called.append("move container to workspace {}".format(target_ws))
    else:
        not_called.append("move container to workspace {}".format(target_ws))

    con_mock.assert_has_calls([mocker.call(cmd) for cmd in called])
    for call in not_called:
        assert call not in con_mock.call_args_list


@pytest.mark.parametrize("is_running", [True, False])
def test_run(is_running, rol, mocker):
    mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "_is_running", return_value=is_running
    )
    handle_running_mock = mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "_handle_running"
    )
    handle_not_running_mock = mocker.patch.object(
        raiseorlaunch.Raiseorlaunch, "_handle_not_running"
    )

    rol.run()

    if is_running:
        handle_running_mock.assert_called_once_with(is_running)
        assert not handle_not_running_mock.called
    else:
        assert handle_not_running_mock.called
        assert not handle_running_mock.called
