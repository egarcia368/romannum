# romannum

A command line tool that converts between integers and roman numerals,
one value per line.

Roman numeral converters are easy to find, but most of them assume the
whole input fits comfortably in a variable. That falls apart the moment
someone hands you a file with a few million lines - a spreadsheet
export, a generated invoice list, whatever. `romannum` reads its input
line by line and writes each result as it goes, so memory use stays
flat no matter how large the file is.

## Usage

Convert integers to roman numerals:

```
$ printf '1994\n58\n3999\n' | romannum to-roman
MCMXCIV
LVIII
MMMCMXCIX
```

Convert roman numerals back to integers:

```
$ printf 'MCMXCIV\nLVIII\n' | romannum from-roman
1994
58
```

Either subcommand also accepts a file path instead of stdin:

```
$ romannum to-roman numbers.txt > roman.txt
```

Lines that fail to convert are reported on stderr with their line
number, and processing continues with the rest of the file:

```
$ printf '1994\nnot-a-number\n58\n' | romannum to-roman
MCMXCIV
LVIII
line 2: 'not-a-number' is not an integer
```

The exit code is 1 if any line failed and 0 otherwise.

If your input isn't newline-separated, pass `--delimiter` with the
string to split on instead:

```
$ printf '1994,58,3999' | romannum to-roman --delimiter ,
MCMXCIV
LVIII
MMMCMXCIX
```

`--delimiter` recognizes the escapes `\n`, `\t`, `\r`, and `\0`, so you
can split on a literal tab without needing shell quoting tricks:

```
$ printf '1994\t58' | romannum to-roman --delimiter '\t'
```

Output is still written one result per line regardless of the input
delimiter.

For csv-style input with several values on each line, use
`--field-separator`. Every field is converted and the line is written
back out joined with the same separator. Empty fields stay empty:

```
$ printf '1994,58\n4,,9\n' | romannum to-roman --field-separator ,
MCMXCIV,LVIII
IV,,IX
```

If any field in a row is invalid, the whole row is skipped and the
error lists each bad field (`line 2: field 1: ...`). It can be combined
with `--delimiter` as long as the two strings differ.

Valid input is a plain integer from 1 to 3999 for `to-roman`, or a
canonical roman numeral (e.g. `IX`, not `VIIII`) for `from-roman`.
Roman numerals have no way to represent zero or negative numbers, and
the classical system stops at 3999.

## Installing

No dependencies beyond the Python standard library.

```
pip install -e .
```

This installs a `romannum` command on your PATH. You can also run it
without installing:

```
python -m romannum.cli to-roman
```

## Testing

```
pip install -e '.[test]'
pytest
```

## License

MIT, see LICENSE.
