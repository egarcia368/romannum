"""Command line entry point.

Both subcommands read their input one line at a time and write each
result as soon as it is ready. Nothing is collected into a list first,
so a multi-gigabyte file costs the same memory as a one-line file.
"""
import argparse
import sys

from . import from_roman, to_roman


def _int_to_roman_line(line):
    try:
        n = int(line)
    except ValueError:
        raise ValueError(f"{line!r} is not an integer")
    return to_roman(n)


def _process(lines, convert, out, err):
    had_error = False
    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            result = convert(line)
        except ValueError as exc:
            print(f"line {lineno}: {exc}", file=err)
            had_error = True
            continue
        out.write(f"{result}\n")
    return had_error


def build_parser():
    parser = argparse.ArgumentParser(
        prog="romannum",
        description="Convert between integers and roman numerals, one value per line.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    to_roman_cmd = sub.add_parser("to-roman", help="read integers, write roman numerals")
    to_roman_cmd.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="file to read (defaults to stdin)",
    )

    from_roman_cmd = sub.add_parser("from-roman", help="read roman numerals, write integers")
    from_roman_cmd.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="file to read (defaults to stdin)",
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    convert = _int_to_roman_line if args.command == "to-roman" else from_roman

    try:
        had_error = _process(args.infile, convert, sys.stdout, sys.stderr)
    finally:
        if args.infile is not sys.stdin:
            args.infile.close()

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
