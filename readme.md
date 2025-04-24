# plxsversion

This is a simple python tool that can be used to create a version file that can be leveraged by a codebase to report consistent versioning. 

## Usage

### CMake Integration

For C/C++ projects is recommended to add this package using CPM and register CMake targets to have version information generated. 

Example CMake to get the package:
```
include(CPM)

CPMAddPackage(
    NAME plxsversion
    GITHUB_REPOSITORY PlexusEP/plxsversion
    GIT_TAG 5ea2b98a70c99ad77ed7296350e3e39213e03b69)
    
include(${plxsversion_SOURCE_DIR}/plxsversion.cmake)
```

Example CMake to generate version for a C++ target:
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

Consider a C application that you wish to use the file `./apps/my_app/version.txt` for the versioning information:
```
target_plxsversion_init(my_app
  LANG c
  SOURCE file
  INPUT ${CMAKE_CURRENT_SOURCE_DIR}/apps/my_app/version.txt
)
```

### Manual Usage

This script should be ran as a python module. To do this:

1. Navigate to this repository's `src` directory or add this directory to the `PYTHONPATH` environment variable
2. Invoke the tool: ```python -m version_builder --lang <output_language> --input <git_dir> <output_file>```

Other parameters can be found in the public interface for the module. 

### Limitations

#### General

- Tool must always run in a git repo regardless of version data source
- Git repo the tool runs in must have at least 1 valid commit

#### Tag Format

The general structure of valid tag formats is based on semantic versioning with an additional descriptor field. This ends up looking like `<major>.<minor>.<patch>-<my>_<descriptor>`. The descriptor field expects an alpha-numeric string that can be separated using underscores. 

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

### Output Data

The created file contains the following information:

| Variable                | Description |
| ----------------------- | ----------- |
| VERSION                 | Complete version including tag and commit specific data |
| VERSION_COMPONENTS      | The semantic major.minor.patch component of the tag |
| VERSION_DESCRIPTOR      | The descriptive component of the tag |
| TAG                     | The raw tag before processing into components |
| COMMITS_SINCE_TAG       | Number of commits since the last tag or 0 if not using git as version data source |
| COMMIT_ID               | Commit ID of the git commit used to build |
| DIRTY_BUILD             | True if the git repo had uncommitted changes at build time |
| DEVELOPMENT_BUILD       | True if MODIFIED_SINCE_COMMIT or commits since last tag |

## Development

This project uses VSCode devcontainers as the development environment. Upon opening the repository in code, re-open it within a devcontainer. This will install the necessary dependencies.

### Code Quality

We use `ruff` to enforce formatting and execute lint of the code base. Formatting should be automatic, but can be checked by running `ruff format`. Linting must be ran manually using `ruff check` or the VSCode task. 

### Unit testing

This project uses `pytest` for unit testing. Simply run `pytest` or the VSCode task to execute UTs. Unit tests can be debugged from the "Testing" tab in VSCode. 
