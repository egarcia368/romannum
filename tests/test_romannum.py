import pytest

from romannum import from_roman, to_roman

KNOWN_PAIRS = [
    (1, "I"),
    (4, "IV"),
    (5, "V"),
    (9, "IX"),
    (14, "XIV"),
    (40, "XL"),
    (49, "XLIX"),
    (58, "LVIII"),
    (90, "XC"),
    (400, "CD"),
    (900, "CM"),
    (1994, "MCMXCIV"),
    (2024, "MMXXIV"),
    (3999, "MMMCMXCIX"),
]


@pytest.mark.parametrize("n, roman", KNOWN_PAIRS)
def test_to_roman_known_values(n, roman):
    assert to_roman(n) == roman


@pytest.mark.parametrize("n, roman", KNOWN_PAIRS)
def test_from_roman_known_values(n, roman):
    assert from_roman(roman) == n


def test_round_trip_full_range():
    for n in range(1, 4000):
        assert from_roman(to_roman(n)) == n


@pytest.mark.parametrize("n", [0, -1, -100, 4000, 10000])
def test_to_roman_out_of_range(n):
    with pytest.raises(ValueError):
        to_roman(n)


@pytest.mark.parametrize("value", ["5", 5.0, None, [1]])
def test_to_roman_rejects_non_int(value):
    with pytest.raises(TypeError):
        to_roman(value)


@pytest.mark.parametrize("value", [True, False])
def test_to_roman_rejects_bool(value):
    with pytest.raises(TypeError):
        to_roman(value)


def test_from_roman_accepts_lowercase_and_surrounding_whitespace():
    assert from_roman("  mcmxciv  ") == 1994


@pytest.mark.parametrize("text", ["", "   "])
def test_from_roman_rejects_empty(text):
    with pytest.raises(ValueError):
        from_roman(text)


@pytest.mark.parametrize("text", ["MCMXCIVQ", "ABC", "1994", "MX9"])
def test_from_roman_rejects_non_roman_characters(text):
    with pytest.raises(ValueError):
        from_roman(text)


@pytest.mark.parametrize(
    "text",
    [
        "IIII",  # non-canonical repetition, should be IV
        "VX",  # invalid subtractive pair
        "IC",  # invalid subtractive pair, should be XCIX
        "IL",  # invalid subtractive pair
        "XM",  # invalid subtractive pair
        "VV",  # V cannot repeat
        "LL",  # L cannot repeat
        "DD",  # D cannot repeat
        "MMMM",  # M cannot repeat more than three times
    ],
)
def test_from_roman_rejects_non_canonical_forms(text):
    with pytest.raises(ValueError):
        from_roman(text)
