import argparse
from version_builder import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a source file containing git version information.")
    parser.add_argument("--lang", "-l", choices=["cpp"], required=True)
    parser.add_argument("--source", "-s", choices=["git", "file"], required=True)
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--print", "-p", action=argparse.BooleanOptionalAction)
    parser.add_argument("path")
    args = parser.parse_args()

    print("Creating version information using %s from %s" % (args.source, args.input))

    main.create_version_file(
        source=args.source,
        source_input=args.input,
        output_path=args.path,
        lang=args.lang,
        print_created_file=args.print,
    )
