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


_ESCAPES = {"\\n": "\n", "\\t": "\t", "\\r": "\r", "\\0": "\0"}


def _unescape_delimiter(delimiter):
    for escaped, literal in _ESCAPES.items():
        delimiter = delimiter.replace(escaped, literal)
    return delimiter


def _iter_fields(fileobj, delimiter, chunk_size=65536):
    """Yield delimiter-separated fields from a file-like object.

    Reads in fixed chunks and splits the accumulated buffer instead of
    reading the whole file up front, so a delimiter that never appears
    (or a huge file) still costs one chunk plus the current field, not
    the whole input.
    """
    buf = ""
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        buf += chunk
        parts = buf.split(delimiter)
        buf = parts.pop()
        for part in parts:
            yield part
    if buf:
        yield buf


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
    to_roman_cmd.add_argument(
        "--delimiter", default=None,
        help="split input on this string instead of newlines (supports \\n, \\t, \\r, \\0)",
    )

    from_roman_cmd = sub.add_parser("from-roman", help="read roman numerals, write integers")
    from_roman_cmd.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="file to read (defaults to stdin)",
    )
    from_roman_cmd.add_argument(
        "--delimiter", default=None,
        help="split input on this string instead of newlines (supports \\n, \\t, \\r, \\0)",
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    convert = _int_to_roman_line if args.command == "to-roman" else from_roman

    if args.delimiter is not None:
        delimiter = _unescape_delimiter(args.delimiter)
        if not delimiter:
            parser.error("--delimiter must not be empty")
        lines = _iter_fields(args.infile, delimiter)
    else:
        lines = args.infile

    try:
        had_error = _process(lines, convert, sys.stdout, sys.stderr)
    finally:
        if args.infile is not sys.stdin:
            args.infile.close()

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
