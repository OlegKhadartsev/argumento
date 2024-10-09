## [1.2.1] - 2024-10-09

### Fixed

- python 3.7 compatibility fix

## [1.2.0] - 2024-09-19

### Added

- ENV variable type resolve syntax: ${ENV_VARIABLE:type|default_value} 


## [1.1.0] - 2024-07-18

### Added

- ENV variable parsing syntax (in .yaml/yml, json, toml): ${ENV_VARIABLE|default_value}


## [1.0.7] - 2024-07-17

### Changed

- manually encoding json file since 'encoding' was removed from json.loads() in Python 3.9 (for python>3.9 support)


## [1.0.6] - 2024-02-21

### Added

- Nice bool args support (e.g. `--my-bool-false False`) 


## [1.0.5] - 2023-06-14

 
### Added

- Hierarchical configs supported
 
### Changed

- Config parser returns _NamespaceDict_ instead of _Namespace_
 
### Fixed


## [1.0.4] - 2023-06-13
 
### Added

### Changed

### Fixed

- Encoding UTF8 in configs 