from version_builder import getter, formatter


def get_version(source, source_input):
    """Obtains version info from a particular data source"""
    match source:
        case "git":
            return getter.from_git(source_input)
        case "file":
            return getter.from_file(source_input)
        case _:
            raise ValueError("Unknown source")


def create_version_file(source, source_input, output_path, lang, print_created_file):
    version_info = get_version(source, source_input)
    _output_version_file(version_info, output_path, lang, print_created_file)


def _output_version_file(version_info, output_path, lang, print_created_file):
    """Converts version info into a requested format and outputs to a file"""
    match lang:
        case "cpp":
            output = formatter.to_cpp(version_info)
            file_extension = ".hpp"
        case "c":
            # TODO-KW
            # output = formatter.to_c(version_info)
            file_extension = ".h"
        case _:
            raise ValueError("Unknown language")

    with open(output_path + "/version" + file_extension, "w") as file:
        file.write(output)

    if print_created_file:
        with open(output_path + "/version" + file_extension, "r") as file:
            print(file.read())
