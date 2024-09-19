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

### ENV variable parsing

Supports parsing of ${ENV_VARIABLES} in strings.    
Syntax: ${ENV_VARIABLE:type|default_value} or just ${ENV_VARIABLE} / ${ENV_VARIABLE:type} / ${ENV_VARIABLE|default_value}.  
If possible ENV_VARIABLE will be resolved as python-valid code strings (with ast.literal_eval()) and typecast to one of:  
   - int (e.g. "5" -> 5)  
   - float ("5.0" -> 5.0)  
   - bool ("True", "t", "yes", etc -> True)  
   - str (to explicitly specify type, if needed)  
Resolving by ast.literal_eval() is useful to set:
   - list ("[1, 'true', 3.0]" -> [1, 'true', 3.0], according to python syntax)
   - dict ("{'a': 123, "b": 'qwe'}" -> {'a': 123, 'b': 'qwe'})
   - tuples
   - ... see ast.literal_eval() docs for more
If type casting of ENV_VARIABLE fails, default_value will also try to be resolved as python-valid string and typecast.    
If both typecasts fail - ENV_VARIABLE will be resolved as is (to string).  
Hint: don't make typos in ENV_VARIABLE setup and there won't be any problems :)  
If ENV_VARIABLE is not set - default_value (string) would be returned.  
If default_value is also not provided - '' (empty string) would be returned as default value.    

Example config.yaml:
```yaml
standalone_env: ${MAX_RETRIES|3}
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

# typecasting examples
int_value: ${LENGTH|3}  # -> LENGTH (e.g. "10") will be resolved to integer value 10
float_value: ${TEMPERATURE}  # -> TEMPERATURE (e.g. "36.0") will be resolved to float value 36.0 
typecast_int: ${LENGTH:float}  # -> LENGTH (e.g. "10") will be resolved to float value 10.0
valid_list: ${PORTS|['default', 'goes', 'here']}  # -> "[1002, 'tennis', 1004.12]" -> [1002, 'tennis', 1004.12]
invalid_list_with_default: ${SPORTS|[1, 2]}  # -> "[football, 123]" -> [1, 2], since default is provided
invalid_list_without_default: ${SPORTS}  # -> "[football, 123]" -> '[football, 123]', string as default is not set
complex_string: '/path/${A}/${B}/folder' # A and B will be resolved, casted back to str and inserted into the string
wrong_type: ${VAR:wrong_type}  # will be resolved (as python code), but not casted (with warning about wrong_type)

```

Important! - parses ${ENV_VARIABLE} to strings (since env. vars are strings).  
Integer/float env.vars/defaults would be set as strings.  
E.g.: batch_size: ${BATCH_SIZE}, where env. variable BATCH_SIZE is set to '1' would be resolved to batch_size == '1'  
(isinstance(batch_size, str) -> True).  


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