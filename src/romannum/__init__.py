"""Conversion between integers and roman numerals."""

_VALUES = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]

_LETTER_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def to_roman(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"expected an int, got {type(n).__name__}")
    if n <= 0 or n > 3999:
        raise ValueError(f"{n} is out of range for roman numerals (1-3999)")
    parts = []
    remaining = n
    for value, symbol in _VALUES:
        if remaining <= 0:
            break
        count, remaining = divmod(remaining, value)
        if count:
            parts.append(symbol * count)
    return "".join(parts)


def from_roman(s):
    text = s.strip().upper()
    if not text:
        raise ValueError("empty string is not a valid roman numeral")
    bad = set(text) - set(_LETTER_VALUES)
    if bad:
        raise ValueError(f"{text!r} contains characters that are not roman numerals: {''.join(sorted(bad))!r}")

    total = 0
    prev_value = 0
    for char in reversed(text):
        value = _LETTER_VALUES[char]
        if value < prev_value:
            total -= value
        else:
            total += value
            prev_value = value

    # Subtractive notation has more invalid strings than valid ones (IIII,
    # VX, IC, ...), so the cheapest correctness check is round-tripping
    # through the encoder rather than hand-writing every forbidden pattern.
    if total <= 0 or total > 3999 or to_roman(total) != text:
        raise ValueError(f"{text!r} is not a valid roman numeral")
    return total
