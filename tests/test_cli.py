import sys
from argparse import ArgumentParser, ArgumentTypeError, Namespace

import pytest

from raiseorlaunch import Raiseorlaunch, __main__ as main


def test_arguments_all(default_args_cli, mocker):
    initial_args = [
        "--class",
        "Coolapp",
        "--instance",
        "instance",
        "--title",
        "title",
        "--workspace",
        "CA",
        "--event-time-limit",
        "7",
        "--ignore-case",
        "--cycle",
        "--leave-fullscreen",
        "--debug",
    ]
    default_args_cli.update(
        {
            "wm_class": "Coolapp",
            "wm_instance": "instance",
            "wm_title": "title",
            "command": "coolapp",
            "workspace": "CA",
            "event_time_limit": 7.0,
            "ignore_case": True,
            "cycle": True,
            "leave_fullscreen": True,
            "debug": True,
        }
    )
    mocker.patch.object(main.os, "access", return_value=True)
    expected_args = Namespace(**default_args_cli)
    args = main.parse_arguments(initial_args)[0]
    assert args == expected_args


def test_verify_app(mocker):
    mocker.patch.object(ArgumentParser, "error")
    assert main.verify_app(ArgumentParser(), "not an executable") == "not an executable"
    ArgumentParser.error.assert_called_with(
        '"not an executable" is not an executable! Did you forget to supply -e?'
    )


def test_set_command_provided(mocker, default_args_cli):
    default_args_cli.update({"command": "ls"})
    args = Namespace(**default_args_cli)
    assert main.set_command(ArgumentParser(), args) == args


def test_set_command_no_executable(mocker, default_args_cli):
    args = Namespace(**default_args_cli)
    mocker.patch.object(ArgumentParser, "error", side_effect=Exception("mocked error"))
    with pytest.raises(Exception) as excinfo:
        main.set_command(ArgumentParser(), args)
    assert str(excinfo.value) == "mocked error"
    ArgumentParser.error.assert_called_with("No executable provided!")


def test_check_time_limit():
    assert main.check_time_limit("3.0") == 3.0
    assert main.check_time_limit("5") == 5.0
    assert main.check_time_limit("13.56") == 13.56

    with pytest.raises(ArgumentTypeError) as excinfo:
        main.check_time_limit("not a float")
    assert str(excinfo.value) == "event-time-limit is not a positive integer or float!"


def test_main(mocker, sys_argv_handler):
    mocker.patch.object(main.os, "access", return_value=True)
    mocker.patch.object(Raiseorlaunch, "__init__")
    mocker.patch.object(Raiseorlaunch, "run")
    Raiseorlaunch.__init__.return_value = None
    sys.argv = ["__main__.py", "-c", "coolapp", "-d"]
    main.main()


def test_main_exception(mocker, sys_argv_handler):
    def side_effect(parser, args):
        return args

    mocker.patch("raiseorlaunch.__main__.set_command", side_effect=side_effect)
    sys.argv = ["__main__.py"]
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.type == SystemExit
    assert str(excinfo.value) == "2"
