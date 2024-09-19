import argparse
import json
import os.path
import os
import re
from abc import ABC, abstractmethod
from ast import literal_eval
from collections import abc
from typing import Union, List, Type
import warnings

import toml
import yaml
import builtins

from argumento.namespace_dict import NamespaceDict


class ResolveWarning(UserWarning):
    pass


class CastingWarning(UserWarning):
    pass


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class EnvResolver:
    def __init__(self):
        self.default_value = ""
        self.pattern = re.compile(r'\$\{(\w+)(?::(\w+))?(?:\|([^}]*))?}')  # pattern: '${NAME:type|default}'

        self.type_map = {
            'int': int,
            'float': float,
            'str': str,
            'bool': lambda v: str2bool(str(v)),
        }

    def _nested_dict_iter(self, nested: abc.Mapping):
        """
        Recursively iterates over nested (optionally) dictionary,
          traversing list-like and dict-like structures,
          yields on leaf nodes (to be processed).
        """
        for key, value in nested.items():
            if isinstance(value, abc.Mapping):
                yield from self._nested_dict_iter(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, abc.Mapping):
                        yield from self._nested_dict_iter(item)
                    else:
                        yield value, i, item
            else:
                yield nested, key, value

    def _resolve_match(self, match):
        """Handles the replacement of a single match from the regex."""
        var_name = match.group(1)  # Environment variable name
        cast_type = match.group(2)  # Optional cast type (e.g., int, float, bool)
        default_value = match.group(3)

        env_value = os.environ.get(var_name, default_value if default_value is not None else self.default_value)

        if not env_value:
            warnings.warn(f"Environment variable '{var_name}' not found and no default provided.", ResolveWarning)
            return env_value

        # Attempt to cast the value to the specified type
        return self._cast_value(env_value, cast_type, default_value)

    def _cast_value(self, value, cast_type, default_value):
        """Casts the value to the specified type, or evaluates literals if no cast_type is specified."""
        try:
            evaluated_value = literal_eval(value)
        except (ValueError, SyntaxError):
            evaluated_value = value

        cast_func = self.type_map.get(cast_type)
        if cast_func is None:
            return evaluated_value

        try:
            return cast_func(evaluated_value)
        except (ValueError, TypeError, AttributeError, argparse.ArgumentTypeError) as e:
            if default_value is not None:
                if cast_type is not None:
                    warnings.warn(f"Cannot cast '{evaluated_value=}' to {cast_type}: {e}, casting {default_value=}",
                                  CastingWarning)
                try:
                    default_value = literal_eval(default_value)
                    return cast_func(default_value)
                except (ValueError, TypeError, SyntaxError) as e_def:
                    if cast_type is not None:
                        warnings.warn(f"Cannot cast '{default_value=}' to {cast_type}: {e_def}, keeping as is",
                                      CastingWarning)
                    return default_value
            if cast_type is not None:
                warnings.warn(f"Cannot cast '{evaluated_value=}' to {cast_type}: {e}, keeping as is",
                              CastingWarning)
            return evaluated_value

    def _parse_string(self, string: str):
        """Pattern-matches string with self.pattern, substitutes match groups with os.environ/default values."""
        all_matches = list(self.pattern.finditer(string))

        # If there is exactly one match and no extra text, return the resolved type
        if len(all_matches) == 1 and string.strip() == all_matches[0].group(0):
            return self._resolve_match(all_matches[0])

        # Otherwise, replace all matches and return the full string
        return self.pattern.sub(lambda match: str(self._resolve_match(match)), string)

    def resolve_envs(self, config: dict) -> dict:
        """Entry point for config (dict) variables recursive env. search and resolve"""
        for container, key, value in self._nested_dict_iter(config):
            if isinstance(value, str):
                container[key] = self._parse_string(value)
        return config


class ParserBase(ABC):
    def __init__(self, config_file: str):
        self._config_file = config_file
        self.env_resolver = EnvResolver()

    @abstractmethod
    def _read_config(self):
        pass

    def parse(self) -> NamespaceDict:
        cfg_file_dict = self._read_config()
        cfg_file_dict = self.env_resolver.resolve_envs(cfg_file_dict)
        cmd_arg_parser = self._cmd_args_from_cfg_keys(cfg_file_dict)
        args, _ = cmd_arg_parser.parse_known_args()
        return NamespaceDict(vars(args))

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
            elif isinstance(v, bool):
                cmd_parser.add_argument(f'--{full_key_name}', type=str2bool, default=v)
            else:
                cmd_parser.add_argument(f'--{full_key_name}', type=type(v), default=v)
        return cmd_parser


class ParserToml(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, 'r', encoding='utf8') as f:
            return toml.load(f)


class ParserYaml(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, 'r', encoding='utf8') as f:
            return yaml.safe_load(f)


class ParserJson(ParserBase):
    def __init__(self, config_file: str):
        super().__init__(config_file)

    def _read_config(self) -> dict:
        with open(self._config_file, 'r', encoding='utf8') as f:
            data = f.read().encode("utf-8")
            return json.loads(data)


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

