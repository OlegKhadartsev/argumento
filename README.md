# Project description

**argumento** is a Python library for reading configuration from config files and command-line args.

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

### ENV variable parsing

Supports parsing of ${ENV_VARIABLES} in strings, to strings.  
Syntax: ${ENV_VARIABLE|default_value} or just ${ENV_VARIABLE}  
If ENV_VARIABLE is not set, `default_value` (string) will be returned.  
If `default_value` is also not provided, the `''` (empty string) will be returned as default value.    

Example config.yaml:
```yaml
standalone_env: ${MAX_RETRIES:3}
embedded_env : 'my_name_is: ${LOGIN|admin}'
multiple_envs: '${ADDRESS}:${PORT|8000}'
list_like: [ '${PORT_1|8000}', '${PORT_2}', '${PORT_3}' ]
different_style:
  - '${PORT_1|8000}'
  - '${PORT_2}'
  - '${PORT_3}'
nested:
  here:
    we:
      go: ${DB_A_ADDRESS|localhost:2233}
just_a_var: 0.5
```

Important! - parses ${ENV_VARIABLE} to strings (since env. vars are strings).  
Integer/float env.vars/defaults will be set as strings.  
E.g.: batch_size: ${BATCH_SIZE}, where env. variable BATCH_SIZE is set to '1' will be resolved to 
batch_size == '1' (isinstance(batch_size, str) -> True).  


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