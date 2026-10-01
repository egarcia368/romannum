import io
import sys

import pytest

from romannum.cli import _convert_fields, _int_to_roman_line, _iter_fields, _process, main, _unescape_delimiter


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


def test_unescape_delimiter_supports_common_escapes():
    assert _unescape_delimiter("\\t") == "\t"
    assert _unescape_delimiter("\\n") == "\n"
    assert _unescape_delimiter(",") == ","


def test_iter_fields_splits_on_arbitrary_delimiter():
    fileobj = io.StringIO("1994,58,3999")
    assert list(_iter_fields(fileobj, ",")) == ["1994", "58", "3999"]


def test_iter_fields_handles_delimiter_split_across_chunks():
    fileobj = io.StringIO("1994,,58")
    assert list(_iter_fields(fileobj, ",,", chunk_size=1)) == ["1994", "58"]


def test_main_with_comma_delimiter(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1994,58,3999"))
    exit_code = main(["to-roman", "--delimiter", ","])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "MCMXCIV\nLVIII\nMMMCMXCIX\n"


def test_convert_fields_keeps_empty_fields():
    assert _convert_fields("1994, ,58", _int_to_roman_line, ",") == "MCMXCIV,,LVIII"


def test_convert_fields_reports_every_bad_field():
    with pytest.raises(ValueError) as info:
        _convert_fields("1,x,3,y", _int_to_roman_line, ",")
    assert "field 2:" in str(info.value)
    assert "field 4:" in str(info.value)


def test_main_field_separator_converts_each_value(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1994,58\n4,9\n"))
    exit_code = main(["to-roman", "--field-separator", ","])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "MCMXCIV,LVIII\nIV,IX\n"


def test_main_field_separator_skips_bad_rows(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("MCMXCIV,LVIII\nIIII,X\nIV,IX\n"))
    exit_code = main(["from-roman", "--field-separator", ","])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == "1994,58\n4,9\n"
    assert "line 2: field 1:" in captured.err


def test_main_field_separator_with_delimiter(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1,2;3,4"))
    exit_code = main(["to-roman", "--delimiter", ";", "--field-separator", ","])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "I,II\nIII,IV\n"


def test_main_rejects_identical_separator_and_delimiter(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1,2"))
    with pytest.raises(SystemExit):
        main(["to-roman", "--delimiter", ",", "--field-separator", ","])
    assert "must differ" in capsys.readouterr().err


def test_main_rejects_empty_delimiter(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("1994"))
    with pytest.raises(SystemExit):
        main(["to-roman", "--delimiter", ""])
    captured = capsys.readouterr()
    assert "must not be empty" in captured.err
