import argparse
import toml
import builtins
from argparse import Namespace

class Parser():
    def __init__(self, config_file: str) -> Namespace:
        self._config_file = config_file

    def parse(self):
        with open(self._config_file, "r") as f:
            cfg_file_dict = toml.load(f)
        cmd_arg_parser = self._cmd_args_from_cfg_keys(cfg_file_dict)
        args, _ = cmd_arg_parser.parse_known_args()
        return args

    @classmethod
    def _cmd_args_from_cfg_keys(cls,
                                cfg_file_dict: dict,
                                parent_cfg_name: str = None,
                                cmd_parser: argparse.ArgumentParser = None
                                ) -> argparse.ArgumentParser:
        if cmd_parser is None:
            cmd_parser = argparse.ArgumentParser()
        for k, v in cfg_file_dict.items():
            full_key_name = k if parent_cfg_name is None else f'{parent_cfg_name}.{k}'
            if isinstance(v, dict):
                # recursion for nested nodes in config
                cls._cmd_args_from_cfg_keys(v, full_key_name, cmd_parser)
            elif isinstance(v, str):
                v_no_space = v.replace(' ', '')
                if v_no_space.startswith('?:'):
                    # required param, not set in the config file, needs top be set in command line
                    type_name = v_no_space[2:]
                    # only list[int], list[float] supported
                    # TODO: list[str]
                    if type_name.startswith('list[') and type_name.endswith(']'):
                        item_type_name = type_name[5:-1]
                        assert item_type_name in ['int', 'float']
                        item_type = getattr(builtins, item_type_name)
                        cmd_parser.add_argument(f'--{full_key_name}',
                                                type=lambda s: [item_type(item) for item in s.split(',')])
                    else:
                        type_ = getattr(builtins, type_name)
                        cmd_parser.add_argument(f'--{full_key_name}', required=True, type=type_)
                else:
                    cmd_parser.add_argument(f'--{full_key_name}', type=str, default=v)
            else:
                cmd_parser.add_argument(f'--{full_key_name}', type=type(v), default=v)
        return cmd_parser


