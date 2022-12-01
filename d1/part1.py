import itertools
from pathlib import Path
from typing import Iterator


def get_lines() -> Iterator[str]:
    path = Path(__file__).parent / "input.txt"
    with path.open() as f:
        for line in f:
            yield line.rstrip()


def get_snacks(lines: Iterator[str]) -> Iterator[Iterator[int]]:
    return (map(int, g) for k, g in itertools.groupby(lines, key=bool) if k)


def run():
    return max(map(sum, get_snacks(get_lines())))
