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


def _convert_fields(line, convert, field_sep):
    """Convert each field of a line and rejoin with the same separator.

    Empty fields pass through untouched so the columns of a sparse csv
    row stay aligned. Every bad field is collected, not just the first,
    so one pass over a file reports everything wrong with a row.
    """
    results = []
    problems = []
    for index, field in enumerate(line.split(field_sep), start=1):
        field = field.strip()
        if not field:
            results.append("")
            continue
        try:
            results.append(str(convert(field)))
        except ValueError as exc:
            problems.append(f"field {index}: {exc}")
    if problems:
        raise ValueError("; ".join(problems))
    return field_sep.join(results)


def _process(lines, convert, out, err, field_sep=None):
    had_error = False
    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            if field_sep is None:
                result = convert(line)
            else:
                result = _convert_fields(line, convert, field_sep)
        except ValueError as exc:
            print(f"line {lineno}: {exc}", file=err)
            had_error = True
            continue
        out.write(f"{result}\n")
    return had_error


def _add_common_arguments(cmd):
    cmd.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="file to read (defaults to stdin)",
    )
    cmd.add_argument(
        "--delimiter", default=None,
        help="split input on this string instead of newlines (supports \\n, \\t, \\r, \\0)",
    )
    cmd.add_argument(
        "--field-separator", default=None,
        help="treat each line as several values split on this string and "
             "convert every one (supports \\n, \\t, \\r, \\0)",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="romannum",
        description="Convert between integers and roman numerals, one value per line.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    _add_common_arguments(
        sub.add_parser("to-roman", help="read integers, write roman numerals")
    )
    _add_common_arguments(
        sub.add_parser("from-roman", help="read roman numerals, write integers")
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    convert = _int_to_roman_line if args.command == "to-roman" else from_roman

    delimiter = None
    if args.delimiter is not None:
        delimiter = _unescape_delimiter(args.delimiter)
        if not delimiter:
            parser.error("--delimiter must not be empty")
        lines = _iter_fields(args.infile, delimiter)
    else:
        lines = args.infile

    field_sep = None
    if args.field_separator is not None:
        field_sep = _unescape_delimiter(args.field_separator)
        if not field_sep:
            parser.error("--field-separator must not be empty")
        if field_sep == delimiter:
            parser.error("--field-separator and --delimiter must differ")

    try:
        had_error = _process(lines, convert, sys.stdout, sys.stderr, field_sep)
    finally:
        if args.infile is not sys.stdin:
            args.infile.close()

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
