from version_builder import version_collector, formatter


def get_version(source, source_input):
    """Obtains version info from a particular data source"""
    match source:
        case "git":
            return version_collector.from_git(source_input)
        case "file":
            return version_collector.from_file(source_input)
        case _:
            raise ValueError("Unknown source")


def create_version_file(source, source_input, output_file, lang, print_created_file):
    version_info = get_version(source, source_input)
    _output_version_file(version_info, output_file, lang, print_created_file)


def _output_version_file(version_info, output_file, lang, print_created_file):
    """Converts version info into a requested format and outputs to a file"""
    match lang:
        case "cpp":
            output = formatter.to_cpp(version_info)
            file_extension = ".hpp"
        case "c":
            output = formatter.to_c(version_info)
            file_extension = ".h"
        case _:
            raise ValueError("Unknown language")

    if not output_file.endswith(file_extension):
        raise ValueError(
            f"Unexpected file ending for lang {lang:s}. Expected: *{file_extension:s}. Got: {output_file:s}"
        )

    with open(output_file, "w") as file:
        file.write(output)

    if print_created_file:
        with open(output_file) as file:
            print(file.read())
