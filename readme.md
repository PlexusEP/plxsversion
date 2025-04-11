# plxsversion

This is a simple python tool that can be leveraged to create a version file to be leveraged by a codebase.

## Usage

### CMake Integration

It is recommended to add this package using CPM and register CMake targets to have version information generated. 

Example CMake to get the package:
```
include(CPM)

CPMAddPackage(
    NAME plxsversion
    GITHUB_REPOSITORY PlexusEP/plxsversion
    GIT_TAG 5ea2b98a70c99ad77ed7296350e3e39213e03b69)
    
include(${plxsversion_SOURCE_DIR}/plxsversion.cmake)
```

Example CMake to generate version for a target:
```
target_plxsversion_init(my_app)
```

The full signature of `target_plxsversion_init` is:
```
target_plxsversion_init(<TARGET>
  [PRINT]                         produced version file will be printed to stdout
  [LANG <output_language>]        select the language supported by the version file
  [SOURCE <version_source>]       choose if version comes from git or file
  [INPUT <version_input_path>]    path to git repo or file to process version from
)
```

### Manual Usage

This script should be ran as a python module. To do this:

1. Navigate to this repository's `src` directory or add this directory to the `PYTHONPATH` environment variable
2. Invoke the tool: ```python -m version_builder --gitdir <repo_dir> --lang <output_language> <output_dir>```

### Limitations

#### Tag Format

The general structure of valid tag formats is based on semantic versioning with an additional human-readable field. This ends up looking like `<major>.<minor>.<patch>-<human>_<readable>`. The human-readable field expects an alpha-numeric string that can be separated using underscores. 

Examples of valid formats:

- 1.2.3
- v1.2.3
- 1.2.3-MyMilestone
- v1.2.3-MyMilestone_RC3

Examples of invalid formats:

- v1.2
- 1.2-MyMilestone
- v1.2.3MyMilestone
- 1.2.3-MyMilestone-RC2
- 1.2.3-MyMilestone.RC2

#### Supported Tag Sources

plxsversion supports tags from the following interfaces:

- git
- file: This expects a single line containing a valid tag per the above section. 

#### Supported Languages

plxsversion creates version files that support these languages:

- C++ (cpp)
- C (c): The header produced with this option is compatible with both C and C++. 

## Development

This project uses VSCode devcontainers as the development environment. Upon opening the repository in code, re-open it within a devcontainer. This will install the necessary dependencies.

### Code Quality

We use `ruff` to enforce formatting and execute lint of the code base. Formatting should be automatic, but can be checked by running `ruff format`. Linting must be ran manually using `ruff check` or the VSCode task. 

### Unit testing

This project uses `pytest` for unit testing. Simply run `pytest` or the VSCode task to execute UTs. Unit tests can be debugged from the "Testing" tab in VSCode. 
