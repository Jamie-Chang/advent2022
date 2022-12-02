import itertools
from typing import Iterator

from common import get_lines


def get_snacks(lines: Iterator[str]) -> Iterator[Iterator[int]]:
    return (map(int, g) for k, g in itertools.groupby(lines, key=bool) if k)


def run():
    return max(map(sum, get_snacks(get_lines(day=1))))
