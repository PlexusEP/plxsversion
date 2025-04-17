from pathlib import PosixPath

from version_builder import formatter, version_collector


def create_version_file(source, source_input, output_file, lang, print_created_file):
    version_info = _get_version(source, source_input)
    _output_version_file(version_info, PosixPath(output_file), lang, print_created_file)


def _get_version(source, source_input):
    """Obtains version info from a particular data source"""
    match source:
        case "git":
            return version_collector.from_git(source_input)
        case "file":
            return version_collector.from_file(source_input)
        case _:
            raise ValueError("Unknown source")


def _output_version_file(version_info, output_file, lang, print_created_file):
    """Converts version info into a requested format and outputs to a file"""
    match lang:
        case "cpp":
            output = formatter.to_cpp(version_info)
            expected_file_extension = ".hpp"
        case "c":
            output = formatter.to_c(version_info)
            expected_file_extension = ".h"
        case _:
            raise ValueError("Unknown language")

    if output_file.suffix != expected_file_extension:
        raise ValueError(
            f"Unexpected file ending for lang {lang:s}. Expected: *{expected_file_extension:s}. Got: {output_file.name:s}"
        )

    with open(output_file, "w") as file:
        file.write(output)

    if print_created_file:
        with open(output_file) as file:
            print(file.read())
