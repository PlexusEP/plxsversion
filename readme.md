# plxsversion

This is a simple python tool that can be used to create a version file that can be leveraged by a codebase to report consistent versioning. 

## Usage

### CMake Integration

For C/C++ projects is recommended to add this package using CPM and register CMake targets to have version information generated. The version information is exposed as a CMake interface library, that can be linked to by multiple targets. 

Example CMake to get the package:
```
include(CPM)

CPMAddPackage(
    NAME plxsversion
    GITHUB_REPOSITORY PlexusEP/plxsversion
    GIT_TAG 5ea2b98a70c99ad77ed7296350e3e39213e03b69)
    
include(${plxsversion_SOURCE_DIR}/plxsversion.cmake)
```

Example CMake to generate version for a C++ project and link to it:
```
plxsversion_create_target()
```

In CMakeLists.txt for `my_app`:
```
target_link_libraries(my_app PRIVATE plxsversion)
```

The full signature of `plxsversion_create_target` is:
```
plxsversion_create_target(
  [PRINT]                         produced version file will be printed to stdout
  [TIME]                          produced version file will contain time data
  [LANG <output_language>]        select the language supported by the version file
  [TARGET_SUFFIX <suffix>]        suffix to append to `plxsversion-` if generating multiple version libraries in a single build
  [SOURCE <version_source>]       choose if version comes from git or file
  [INPUT <version_input_path>]    path to git repo or file to process version from
)
```

Consider a C application that you wish to use the file `./apps/my_app/version.txt` for the versioning information and for `my_app`:
```
plxsversion_create_target(
  LANG c
  TARGET_SUFFIX my_app
  SOURCE file
  INPUT ${CMAKE_CURRENT_SOURCE_DIR}/apps/my_app/version.txt
)
```

In CMakeLists.txt for `my_app`:
```
target_link_libraries(my_app PRIVATE plxsversion-my_app)
```

### Manual Usage

This script can be run as a Python module. To do this:

1. Navigate to this repository's `src` directory or add this directory to your `PYTHONPATH` environment variable.
2. Invoke the tool using the following command structure:
   ```bash
   python -m version_builder --source <source_type> --lang <language> --input <path_to_source> <output_file>
   ```

Here are the available arguments:

| Argument | Short | Description | Required |
|---|---|---|---|
| `--source` | `-s` | Type of source for version info (`git` or `file`). | Yes |
| `--lang` | `-l` | Language for the output file (`cpp`, `cpp11`, `c`). | Yes |
| `--input` | `-i` | Path to the source of version information. | Yes |
| `file` | | Path for the generated output file. | Yes |
| `--print` | `-p` | Print the generated file's contents after creation. | No |
| `--time` | `-t` | Include timestamp data in the version information. | No |

**Example using `git` as a source:**

This command generates a C++ header file (`version.hpp`) from the git history of the current directory (`.`) and prints its contents.

```bash
python -m version_builder --source git --lang cpp --input . --print version.hpp
```

**Example using `file` as a source:**

This command generates a C header file (`version.h`) using a version tag from `./version.txt`.

```bash
python -m version_builder --source file --lang c --input ./version.txt version.h
```

### Limitations

#### General

- Tool must always run in a git repo regardless of version data source
- Git repo the tool runs in must have at least 1 valid commit

#### Tag Format
This tool expects git tags to follow Semantic Versioning 2.0.0 (SemVer).
The version string itself should be of the form `X.Y.Z[-PRERELEASE][+BUILD_METADATA]`.
A leading `v` (e.g., `v1.2.3`) in the git tag is permitted and will be stripped by the tool before parsing the SemVer string. PRERLEASE and BUILD_METADATA are optional for a tag. They can be used to provide addtional contextual data about a build which would be incorporated into a version string. 

- **PRERELEASE**: A series of dot-separated identifiers. Identifiers are composed of ASCII alphanumerics and hyphens. Numeric identifiers MUST NOT have leading zeros (e.g., `1.0.0-alpha.1`, `1.0.0-rc.2`, `1.0.0-MyMilestone`).
- **BUILD_METADATA**: A series of dot-separated identifiers. Identifiers are composed of ASCII alphanumerics and hyphens (e.g., `1.0.0+build.123`, `1.0.0-alpha+007.exp`).

Examples of valid formats:

- 1.2.3
- v1.2.3
- 1.0.0-alpha
- v1.0.0-alpha.1
- 1.0.0-beta+build.123.abc
- 0.0.1-SNAPSHOT.12

Examples of invalid formats:

- v1.2
- 1.2.3-My_Milestone (underscores are not allowed in pre-release or build metadata identifiers)
- 1.2.3-alpha..beta (empty pre-release identifier)
- 1.0.0-01 (leading zero in numeric pre-release identifier)

#### Supported Tag Sources

plxsversion supports tags from the following interfaces:

- git
- file: This expects a single line containing a valid tag per the above section. 

#### Supported Languages

plxsversion creates version files that support these languages:

- C++ (cpp): The header produced requires C++17 or newer. No dynamic allocation is used. 
- C++11 (cpp11): The header produced requires C++11 or newer. No dynamic allocation is used. 
- C (c): The header produced with this option is compatible with both C and C++. No dynamic allocation is used. 

### Output Data

The created file contains the following information:

| Variable                | Description |
| ----------------------- | ----------- |
| VERSION                 | Complete version including tag and commit specific data |
| MAJOR                   | The semantic major component of the tag |
| MINOR                   | The semantic minor component of the tag |
| PATCH                   | The semantic patch component of the tag |
| PRE_RELEASE             | The pre-release component of the tag |
| BUILD_METADATA          | The metadata component of the tag |
| TAG                     | The raw tag before processing |
| COMMITS_SINCE_TAG       | Number of commits since the last tag (defaults to 0 if using file for semantic version) |
| COMMIT_ID               | Commit ID of the git commit used to build |
| BRANCH                  | Branch of the source used to build |
| DIRTY_BUILD             | True if the git repo had uncommitted changes at build time |
| DEVELOPMENT_BUILD       | True if DIRTY_BUILD or commits since last tag > 0 |
| UTC_TIME                | UTC time of the latest CMake configuration in "YYYY-MM-DD HH:MM" format |

> [!WARNING]  
> Including time data will cause CMake targets relying on the version target to be re-build ANY time a CMake configure happens, even if your code doesn't change. 

Here is an example output version.hpp file for a C++ application tagged `2.1.0` in a dirty checkout

```
// ---------------------------------------------------
// This file is autogenerated.
// DO NOT MODIFY!
// ---------------------------------------------------

#ifndef PLXSVERSION_VERSION_HPP
#define PLXSVERSION_VERSION_HPP

#include <cstdint>
#include <string_view>

namespace plxsversion {

inline constexpr std::string_view VERSION { "2.1.0+dd4c559.dirty" };
inline constexpr unsigned int MAJOR { 2 };
inline constexpr unsigned int MINOR { 1 };
inline constexpr unsigned int PATCH { 0 };
inline constexpr std::string_view PRE_RELEASE { "" };
inline constexpr std::string_view BUILD_METADATA { "" };
inline constexpr std::string_view TAG { "2.1.0" };
inline constexpr unsigned int COMMITS_SINCE_TAG { 0 };
inline constexpr std::string_view COMMIT_ID { "dd4c559" };
inline constexpr std::string_view BRANCH { "master" };
inline constexpr bool DIRTY_BUILD { true };
inline constexpr bool DEVELOPMENT_BUILD { true };
inline constexpr std::string_view UTC_TIME { "2025-05-01 18:21" };

} // namespace plxsversion

#endif // PLXSVERSION_VERSION_HPP
```


## Development

This project uses VSCode devcontainers as the development environment. Upon opening the repository in code, re-open it within a devcontainer. This will install the necessary dependencies.

### Code Quality

We use `ruff` to enforce formatting and execute lint of the code base. Formatting should be automatic, but can be checked by running `ruff format`. Linting must be ran manually using `ruff check` or the VSCode task. 

### Unit testing

This project uses `pytest` for unit testing. Simply run `pytest` or the VSCode task to execute UTs. Unit tests can be debugged from the "Testing" tab in VSCode. 

#### CMake Interface testing

There is no automated testing for CMake at this time. A developer should do manual testing of the following:

- C++17 or newer project can leverage `lang=cpp`, `lang=cpp11`, and `lang=c`
- C++11 or newer project can leverage `lang=cpp11` and `lang=c`
- C project can leverage `lang=c`
- Generate version from git
- Generate version from file
- Library with suffix
- `PRINT` causes created file to print
- `TIME` causes time data in the version file

Here is a sample of CMake implementation that can help test the above cases:

```
# C++17 and up
# plxsversion_create_target(LANG cpp)

# C++11 and up
# plxsversion_create_target(LANG cpp11)

# C
# plxsversion_create_target(LANG c)

# version from git
# plxsversion_create_target(SOURCE git VER_INPUT ${CMAKE_CURRENT_SOURCE_DIR})

# version from file
# plxsversion_create_target(SOURCE file INPUT ${CMAKE_CURRENT_SOURCE_DIR}/version.txt)

# library with suffix
# plxsversion_create_target(TARGET_SUFFIX app_name)
# if(TARGET plxsversion-app_name)
#   # Target exists
#   message(STATUS "Custom target exists.")
# endif()
# if(TARGET plxsversion)
#   message(STATUS "Default target still exists.")
# endif()

# test PRINT
# plxsversion_create_target(PRINT)

# test TIME
# plxsversion_create_target(TIME)
```
