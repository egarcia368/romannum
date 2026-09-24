import io
import sys

import pytest

from romannum.cli import _int_to_roman_line, _process, main


def test_int_to_roman_line_converts():
    assert _int_to_roman_line("1994") == "MCMXCIV"


def test_int_to_roman_line_rejects_non_integer():
    with pytest.raises(ValueError):
        _int_to_roman_line("not-a-number")


def test_process_writes_results_and_skips_blank_lines():
    out = io.StringIO()
    err = io.StringIO()
    had_error = _process(["1994\n", "\n", "58\n"], _int_to_roman_line, out, err)
    assert had_error is False
    assert out.getvalue() == "MCMXCIV\nLVIII\n"
    assert err.getvalue() == ""


def test_process_reports_line_number_and_continues():
    out = io.StringIO()
    err = io.StringIO()
    had_error = _process(["1994\n", "oops\n", "58\n"], _int_to_roman_line, out, err)
    assert had_error is True
    assert out.getvalue() == "MCMXCIV\nLVIII\n"
    assert "line 2:" in err.getvalue()


def test_main_to_roman_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1994\n58\n"))
    exit_code = main(["to-roman"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "MCMXCIV\nLVIII\n"


def test_main_from_roman_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("MCMXCIV\nLVIII\n"))
    exit_code = main(["from-roman"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "1994\n58\n"


def test_main_returns_nonzero_and_reports_bad_lines(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1994\nnot-a-number\n58\n"))
    exit_code = main(["to-roman"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == "MCMXCIV\nLVIII\n"
    assert "line 2:" in captured.err


def test_main_reads_from_file_argument(tmp_path, capsys):
    infile = tmp_path / "numbers.txt"
    infile.write_text("1994\n58\n")
    exit_code = main(["to-roman", str(infile)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "MCMXCIV\nLVIII\n"
