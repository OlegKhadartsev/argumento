import sys
from unittest import mock
import config_args


def test_flat():
    cfg_filename = 'data/flat.toml'
    args = config_args.Parser(cfg_filename).parse()

    assert args.login == "my_login"
    assert args.max_retries == 5
    assert args.ports == [8000, 8001, 8002]
    assert args.ratio == 0.5


def test_flat_cmd_override():
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3']
    with mock.patch.object(sys, 'argv', cmd_args):
        cfg_filename = 'data/flat.toml'
        args = config_args.Parser(cfg_filename).parse()

        # these args were overridden in command-line
        assert args.login == "login_from_cmd"
        assert args.max_retries == 3

        # these args were read from config file
        assert args.ports == [8000, 8001, 8002]
        assert args.ratio == 0.5



def test_redundant_cmd_args():
    """
    should not FAIL if args in command line are not specified in config file
    :return:
    :rtype:
    """
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3', '--redundant-arg', '123']
    with mock.patch.object(sys, 'argv', cmd_args):
        cfg_filename = 'data/flat.toml'
        args = config_args.Parser(cfg_filename).parse()


def test_flat_cmd_only():
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3', '--ratio', '0.2', '--ports', '5000,5001',
                '--fractions', '0.1, 0.2']
    with mock.patch.object(sys, 'argv', cmd_args):
        cfg_filename = 'data/flat_cmd_only.toml'
        args = config_args.Parser(cfg_filename).parse()

        assert args.login == "login_from_cmd"
        assert args.max_retries == 3
        assert args.ratio == 0.2
        assert args.ports == [5000, 5001]
        assert args.fractions == [0.1, 0.2]


"""
#TODO:
1. test hierarchy

"""

