import argparse

from version_builder import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a source file containing git version information.")
    parser.add_argument("--lang", "-l", choices=["cpp", "c"], required=True)
    parser.add_argument("--source", "-s", choices=["git", "file"], required=True)
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--print", "-p", action=argparse.BooleanOptionalAction)
    parser.add_argument("file")
    args = parser.parse_args()

    # Intentional print for user status notification
    print(f"Creating version information using {args.source:s} from {args.input:s}")  # noqa: T201

    main.create_version_file(
        source=args.source,
        source_input=args.input,
        output_file=args.file,
        lang=args.lang,
        print_created_file=args.print,
    )
