from pathlib import PosixPath

from version_builder import formatter, version_collector, version_data


class OptionalConfiguration:
    def __init__(self, *, print_created_file: bool = False, include_time: bool = False) -> None:
        self.print_created_file = print_created_file
        self.include_time = include_time


def create_version_file(
    source: str, source_input: str, output_file: str, lang: str, *, optional_config: OptionalConfiguration = None
) -> None:
    if optional_config is None:
        optional_config = OptionalConfiguration()

    version_info = _get_version(source, source_input)
    if optional_config.include_time:
        version_info.set_time()

    _output_version_file(
        version_info=version_info,
        output_file=PosixPath(output_file),
        lang=lang,
        print_created_file=optional_config.print_created_file,
    )


def _get_version(source: str, source_input: str) -> version_data.VersionData:
    """Obtain version data from a particular data source."""
    match source:
        case "git":
            return version_collector.from_git(source_input)
        case "file":
            return version_collector.from_file(source_input)
        case _:
            msg = "Unknown source"
            raise ValueError(msg)


def _output_version_file(
    version_info: version_data.VersionData, output_file: str, lang: str, *, print_created_file: bool
) -> None:
    """Convert version info into a requested format and outputs to a file."""
    match lang:
        case "cpp":
            output = formatter.to_cpp(version_info)
            expected_file_extension = ".hpp"
        case "cpp11":
            output = formatter.to_cpp11(version_info)
            expected_file_extension = ".hpp"
        case "c":
            output = formatter.to_c(version_info)
            expected_file_extension = ".h"
        case _:
            msg = "Unknown language"
            raise ValueError(msg)

    if output_file.suffix != expected_file_extension:
        msg = (
            f"Unexpected file ending for lang {lang:s}. Expected: *{expected_file_extension:s}. "
            "Got: {output_file.name:s}"
        )
        raise ValueError(msg)

    with open(output_file, "w") as file:
        file.write(output)

    if print_created_file:
        with open(output_file) as file:
            # Intentional printing of file contents
            print(file.read())  # noqa: T201
