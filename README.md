# Project description

**config-args** is a Python library for reading configuration from config files and command-line args.

## Installation

```bash
pip install argumento
```

## Usage

You can define configuration parameters both in config files and in command-line arguments.  
Command-line args have higher priority: param values from command line overwrite values from config files.

Supported config file formats are:

- yaml (.yaml, .yml)
- toml (.toml)
- json (.json)

Basic example:

```python
import argumento

cfg_filename = 'my_config.yaml'
args = argumento.create_parser(cfg_filename).parse()
```

If a parameter is required but is not set in config file, `?:` followed by type name is used instead of a value:

```yaml
login: "?:str"
max_retries: "?:int"
ratio: "?:float"
ports: "?:list[int]"
fractions: "?:list[float]"
```

Supported data types are:

- str
- int
- float
- list\[int]
- list\[float]