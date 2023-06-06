import argparse
import json
import os.path
from abc import ABC, abstractmethod
from typing import Union, List, Iterable, Type
import warnings

import toml
import yaml
import builtins
from argparse import Namespace


class ParserBase(ABC):
    def __init__(self, config_file: str):
        self._config_file = config_file

    @abstractmethod
    def _read_config(self):
        pass

    def parse(self) -> Namespace:
        cfg_file_dict = self._read_config()
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


class ParserToml(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, "r") as f:
            return toml.load(f)


class ParserYaml(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, "r") as f:
            return yaml.safe_load(f)


class ParserJson(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, "r") as f:
            return json.loads(f.read(), encoding='utf8')


class ParserFactory:
    def __init__(self):
        self._parsers = {}

    def _register_single_format(self, fmt: str, parser: Type[ParserBase]):
        if fmt in self._parsers:
            warnings.warn(f'Format {fmt} is already bound to {self._parsers[fmt]}. The value will be overwritten!')
        self._parsers[fmt] = parser

    def register_format(self, fmt: Union[str, List[str]], parser_type: Type[ParserBase]):
        if isinstance(fmt, str):
            self._register_single_format(fmt, parser_type)
        elif isinstance(fmt, list) and all(isinstance(x, str) for x in fmt):
            for fmt_item in fmt:
                self._register_single_format(fmt_item, parser_type)
        else:
            raise ValueError(f'Invalid format: {fmt}')

    def get_parser(self, filename: str) -> ParserBase:
        ext = os.path.splitext(filename)[1]
        if ext.startswith('.'):
            ext = ext[1:]
        parser_type = self._parsers.get(ext)
        if not parser_type:
            raise ValueError(f'Could not infer parser from file type. Unknown file format: "{ext}". '
                             f'Supported formats are: {list(self._parsers.keys())}.')
        return parser_type(filename)


factory = ParserFactory()
factory.register_format(['yml', 'yaml'], ParserYaml)
factory.register_format('toml', ParserToml)
factory.register_format('json', ParserJson)

create_parser = factory.get_parser

