import sys
import os
import pytest
from unittest import mock
from argumento import create_parser


EXTENSIONS = ['toml', 'yaml', 'yml', 'json']


def locate_data_file(filename):
    return os.path.join('tests', 'data', filename)


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat(ext):
    cfg_filename = locate_data_file(f'flat.{ext}')
    args = create_parser(cfg_filename).parse()

    assert args.login == "my_login"
    assert args.max_retries == 5
    assert args.ports == [8000, 8001, 8002]
    assert args.ratio == 0.5


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat_cmd_override(ext):
    cfg_filename = locate_data_file(f'flat.{ext}')
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3',
                '--nice_bool_false', 'False', '--nice_bool_true', 'true']
    with mock.patch.object(sys, 'argv', cmd_args):
        args = create_parser(cfg_filename).parse()

        # these args were overridden in command-line
        assert args.login == "login_from_cmd"
        assert args.max_retries == 3
        assert args.nice_bool_false == False
        assert args.nice_bool_true == True

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
        args = create_parser(cfg_filename).parse()


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_flat_cmd_only(ext):
    cfg_filename = locate_data_file(f'flat_cmd_only.{ext}')
    cmd_args = ['', '--login', 'login_from_cmd', '--max_retries', '3', '--ratio', '0.2', '--ports', '5000,5001',
                '--fractions', '0.1, 0.2']
    with mock.patch.object(sys, 'argv', cmd_args):

        args = create_parser(cfg_filename).parse()

        assert args.login == "login_from_cmd"
        assert args.max_retries == 3
        assert args.ratio == 0.2
        assert args.ports == [5000, 5001]
        assert args.fractions == [0.1, 0.2]


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_hierarch(ext):
    cfg_filename = locate_data_file(f'hierarch.{ext}')
    args = create_parser(cfg_filename).parse()

    assert args.database == {"ports": [8000, 8001, 8002], "connection_max": 5000, "enabled": True}
    assert args['database'] == args.database
    assert args.database.ports == [8000, 8001, 8002]
    assert args.database.ports == args.database['ports']
    assert args.database.ports == args['database'].ports
    assert args.database.ports == args['database.ports']
    assert args.database.connection_max == 5000
    assert args.database.connection_max == args.database['connection_max']
    assert args.database.connection_max == args['database'].connection_max
    assert args.database.connection_max == args['database.connection_max']

    assert args.database.enabled == True

    assert args.servers.alpha == {'ip': '10.0.0.1', 'dc': 'abcd'}
    assert args.servers.alpha.ip == '10.0.0.1'
    assert args.servers.alpha.dc == 'abcd'

    assert args.servers.beta == {'ip': '10.0.0.2', 'dc': 'efgh'}
    assert args.servers.beta.ip == '10.0.0.2'
    assert args.servers.beta.dc == 'efgh'

# TODO: test hierarchical config - overwrite params in cmd


def setup_env():
    os.environ['PORT_1'] = '8000'
    os.environ['PORT_2'] = '8001'
    os.environ['PORT_3'] = '8002'
    os.environ['ENABLED'] = 'True'
    # os.environ['DISABLED'] = 'False'  # not set in ENV - should be None
    os.environ['CONNECTION_MAX'] = '5000'

    os.environ['IP_ALPHA'] = '10.0.0.1'
    os.environ['DC_ALPHA'] = 'ab cd'
    # os.environ['IP_BETA'] = '10.0.0.1:1337'  # not set in ENV
    os.environ['DC_BETA'] = 'xyz'

    # casting tests
    os.environ['STRING_VAR'] = 'qwerty'
    os.environ['LIST_VAR'] = '[1, 2, 3]'
    os.environ['FLOAT_LIST_VAR'] = '[1.0, 2.0, 3.0]'
    os.environ['BOOL_LIST_VAR'] = '[True, False, True]'
    os.environ['MIXED_LIST_VAR'] = "[1.0, True, 3, 'qwe']"
    os.environ['UNCASTABLE_LIST_VAR'] = '[1, true]'
    os.environ['DICT_VAR'] = '{"key": "value"}'
    os.environ['PROPER_BOOL_VAR'] = 'True'
    os.environ['OTHER_BOOL_VAR'] = 'true'
    os.environ['INT_BOOL_VAR'] = '1'
    os.environ['INT_VAR'] = '123'
    os.environ['FLOAT_VAR'] = '124.0'


@pytest.mark.filterwarnings("ignore")
@pytest.mark.parametrize('ext', EXTENSIONS)
def test_env(ext):
    setup_env()
    cfg_filename = locate_data_file(f'env.{ext}')
    args = create_parser(cfg_filename).parse()

    assert args.database == {"ports": [8000, 8001, 8002],
                             "ports_other": [8000, 8001, 8002],
                             "enabled": True, "disabled": '',
                             "connection_max": 5000}
    assert args['database'] == args.database
    assert args.database.ports == [8000, 8001, 8002]
    assert args.database.ports == args.database['ports']
    assert args.database.ports == args['database'].ports
    assert args.database.ports == args['database.ports']
    assert args.database.connection_max == 5000
    assert args.database.connection_max == args.database['connection_max']
    assert args.database.connection_max == args['database'].connection_max
    assert args.database.connection_max == args['database.connection_max']

    assert args.database.enabled == True
    assert args.servers.alpha == {'ip': '10.0.0.1', 'dc': 'path/ab cd/other_path/qwe'}
    assert args.servers.alpha.ip == '10.0.0.1'
    assert args.servers.alpha.dc == "path/ab cd/other_path/qwe"

    assert args.servers.beta == {'ip': '10.0.0.2:1337', 'dc': 'path/xyz/other_path'}
    assert args.servers.beta.ip == '10.0.0.2:1337'
    assert args.servers.beta.dc == "path/xyz/other_path"


@pytest.mark.parametrize('ext', EXTENSIONS)
def test_env_casting(ext):
    setup_env()
    cfg_filename = locate_data_file(f'env.{ext}')
    with pytest.warns(UserWarning):
        args = create_parser(cfg_filename).parse()

    # casting tests
    assert args.casting.int_ok == 123
    assert args.casting.float_ok == float(124.0)
    assert args.casting.bool_ok == True
    assert args.casting.list_ok == [1, 2, 3]
    assert args.casting.dict_ok == {"key": "value"}
    assert args.casting.mixed_list_ok == [1.0, True, 3, 'qwe']

    assert args.casting.uncastable_with_default == 'default_string'
    assert args.casting.uncastable_without_default == 'qwerty'
    assert args.casting.uncastable_list_default == '[1, true]'
    assert args.casting.int_cast == 124
    assert args.casting.float_cast == float(123.0)

    assert args.casting.list_cast == [1.0, 2.0, 3.0]
    assert args.casting.uncastable_list_default_cast == [1, 2, 3]
    assert args.casting.uncastable_list_default_cast_string == '[1, another_uncastable, 3]'
    assert args.casting.bool_cast == True
    assert args.casting.string_cast_default == 123
    assert args.casting.string_cast_forced == '123'
    assert args.casting.string_cast_forced_default == '124.0'
    assert args.casting.unexpected_type_cast == 123
    assert args.casting.unexpected_type_cast_default == 123  # Not 125! Had to compromise.


