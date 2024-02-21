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

### Basic example

```python
import argumento

cfg_filename = 'my_config.yaml'
args = argumento.create_parser(cfg_filename).parse()
```

my_config.yaml:
```yaml
login: "my_login"
max_retries: 5
ports: [ 8000, 8001, 8002 ]
ratio: 0.5
nice_bool_false: False
nice_bool_true: True

```

command line:
```commandline
<command> --login my_login --max_retries 5 --ports: [ 8000, 8001, 8002 ] \
--ratio 0.5 --nice_bool_false False --nice_bool_true True
```

### Bool arguments
Note that **bool** args should be set in command line via 'nice' but non-canonical way.

Supported usage:
```commandline
--nice_bool_false False --nice_bool_true True
```
or 
```commandline
--nice_bool_false false --nice_bool_true true
```


Not supported usage:

`--feature` / `--no-feature` style.

### Required params not defined in config

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