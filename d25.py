from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path

from common import read_lines

TO_DECIMAL = {
    "2": 2,
    "1": 1,
    "0": 0,
    "-": -1,
    "=": -2,
}
TO_SNAFU: dict[int, str] = {
    2: "2",
    1: "1",
    0: "0",
    -1: "-",
    -2: "=",
}


@dataclass
class Snafu:
    value: str

    def __add__(self, other: Snafu) -> Snafu:
        pairs = zip_longest(
            reversed(self.value),
            reversed(other.value),
            fillvalue="0",
        )
        carry_over = "0"

        value = ""
        for d1, d2 in pairs:
            d, carry_over = add_digit(d1, d2, carry_over)
            value = d + value

        if carry_over != "0":
            value = carry_over + value
        return Snafu(value)


def add_digit(a: str, b: str, carry_over: str = "0") -> tuple[str, str]:
    """
    >>> add_digit("2", "2", "1")
    ('0', '1')

    >>> add_digit("=", "=", "-")
    ('0', '-')
    """

    result = TO_DECIMAL[a] + TO_DECIMAL[b] + TO_DECIMAL[carry_over]

    if result > 2:
        return TO_SNAFU[result - 5], TO_SNAFU[1]

    if result < -2:
        return TO_SNAFU[result + 5], TO_SNAFU[-1]

    return TO_SNAFU[result], TO_SNAFU[0]


def run(data: Path):
    return sum(map(Snafu, read_lines(data)), start=Snafu("0")).value
