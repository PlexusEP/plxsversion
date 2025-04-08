import argparse
from version_builder import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a source file containing git version information.")
    parser.add_argument("--lang", "-l", choices=["cpp"], required=True)
    parser.add_argument("--gitdir", "-g", required=True)
    parser.add_argument("--print", "-p", action=argparse.BooleanOptionalAction)
    parser.add_argument("path")
    args = parser.parse_args()

    print("Creating git version information from %s" % args.gitdir)

    main.create_version_file_from_git(
        git_directory=args.gitdir, output_path=args.path, lang=args.lang, print_created_file=args.print
    )
