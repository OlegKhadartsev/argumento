import sys
import os
from unittest import mock

import pytest

import config_args


EXTENSIONS = ['toml', 'yaml', 'yml', 'json']


def locate_data_file(filename):
    return os.path.join('tests', 'data', filename)




@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat(ext):
    cfg_filename = locate_data_file(f'flat.{ext}')
    args = config_args.create_parser(cfg_filename).parse()

    assert args.login == "my_login"
    assert args.max_retries == 5
    assert args.ports == [8000, 8001, 8002]
    assert args.ratio == 0.5


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat_cmd_override(ext):
    cfg_filename = locate_data_file(f'flat.{ext}')
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3']
    with mock.patch.object(sys, 'argv', cmd_args):
        args = config_args.create_parser(cfg_filename).parse()

        # these args were overridden in command-line
        assert args.login == "login_from_cmd"
        assert args.max_retries == 3

        # these args were read from config file
        assert args.ports == [8000, 8001, 8002]
        assert args.ratio == 0.5


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_redundant_cmd_args(ext):
    """
    should not FAIL if args in command line are not specified in config file
    :return:
    :rtype:
    """
    cfg_filename = locate_data_file(f'flat.{ext}')
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3', '--redundant-arg', '123']
    with mock.patch.object(sys, 'argv', cmd_args):
        args = config_args.create_parser(cfg_filename).parse()


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat_cmd_only(ext):
    cfg_filename = locate_data_file(f'flat_cmd_only.{ext}')
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3', '--ratio', '0.2', '--ports', '5000,5001',
                '--fractions', '0.1, 0.2']
    with mock.patch.object(sys, 'argv', cmd_args):

        args = config_args.create_parser(cfg_filename).parse()

        assert args.login == "login_from_cmd"
        assert args.max_retries == 3
        assert args.ratio == 0.2
        assert args.ports == [5000, 5001]
        assert args.fractions == [0.1, 0.2]




#TODO: test hierarchy



