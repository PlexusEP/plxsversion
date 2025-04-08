from version_builder import getter, formatter


def get_version_from_git(git_directory):
    return getter.from_git(git_directory)


def get_version_from_file(file_path):
    return getter.from_file(file_path)


def create_version_file_from_git(git_directory, output_path, lang, print_created_file):
    version_info = get_version_from_git(git_directory)
    _output_version_file(version_info, output_path, lang, print_created_file)


def create_version_file_from_file(file_path, output_path, lang, print_created_file):
    version_info = get_version_from_file(file_path)
    _output_version_file(version_info, output_path, lang, print_created_file)


# def get_version():
#     return True

# def create_version_file(source, source_input, output_path, lang):
#     return True


def _output_version_file(version_info, output_path, lang, print_created_file):
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
