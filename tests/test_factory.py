import pytest

import argumento


def test_unknown_format():
    # .ini not supported
    with pytest.raises(ValueError) as exc_info:
        argumento.create_parser('my_file.ini').parse()

    assert exc_info.value.args[0] == "Could not infer parser from file type. Unknown file format: \"ini\". " \
                                     "Supported formats are: ['yml', 'yaml', 'toml', 'json']."


def test_reqister_custom_parser(tmp_path):

    class ParserCustomTest(argumento.parsers.ParserBase):
        """

        custom cfg format:

        key1: value1
        key2: value2
        ...

        """
        def __init__(self, config_file: str):
            super().__init__(config_file)

        def _read_config(self) -> dict:
            with open(self._config_file, "r") as f:
                lines = [l for l in f if ':' in l]
                return dict([x.strip() for x in l.split(':')] for l in lines)

    # assert argumento.create_parser is argumento.factory.get_parser

    factory = argumento.parsers.ParserFactory()
    factory.register_format('custom', ParserCustomTest)

    cfg_filename = "cfg.custom"

    d = tmp_path / "sub"
    d.mkdir()
    p = d / cfg_filename
    content = """
    key1: value1
    key2: value2
    """
    p.write_text(content)

    cfg = factory.get_parser(p).parse()
    assert vars(cfg) == {'key1': 'value1', 'key2': 'value2'}
