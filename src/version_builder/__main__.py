import argparse

from version_builder import main


def execute() -> None:
    parser = argparse.ArgumentParser(description="Create a source file containing git version information.")
    parser.add_argument(
        "--lang",
        "-l",
        choices=["cpp", "cpp11", "c", "rust"],
        required=True,
        help="language supported by the file output",
    )
    parser.add_argument(
        "--source",
        "-s",
        choices=["git", "file"],
        required=True,
        help="type of source used for generating the version information",
    )
    parser.add_argument("--input", "-i", required=True, help="path to source of version information")
    parser.add_argument(
        "--print",
        "-p",
        action=argparse.BooleanOptionalAction,
        help="print the contents of the generated file after creation",
    )
    parser.add_argument(
        "--time",
        "-t",
        action=argparse.BooleanOptionalAction,
        help="include time data in the version infomation",
    )
    parser.add_argument(
        "--cargo",
        "-c",
        required=False,
        help="cargo version of a crate",
    )
    parser.add_argument("file")
    args = parser.parse_args()

    if args.cargo and args.lang != "rust":
        parser.error("The --cargo argument requires --lang to be set to 'rust'")

    # Intentional print for user status notification
    print(f"Creating version information using {args.source:s} from {args.input:s}")  # noqa: T201

    main.create_version_file(
        source=args.source,
        source_input=args.input,
        output_file=args.file,
        lang=args.lang,
        optional_config=main.OptionalConfiguration(
            print_created_file=args.print, include_time=args.time, cargo_version=args.cargo
        ),
    )


if __name__ == "__main__":
    execute()
