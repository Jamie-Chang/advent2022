from pathlib import Path
from typing import Iterator


def get_lines() -> Iterator[str]:
    path = Path(__file__).parent / "input.txt"
    with path.open() as f:
        for line in f:
            yield line.rstrip()


def get_snacks(lines: Iterator[str]) -> Iterator[list[int]]:
    snacks = []
    for line in lines:
        if line:
            snacks.append(int(line))

        else:
            yield snacks
            snacks = []

    if snacks:
        yield snacks


def run():
    return max(map(sum, get_snacks(get_lines())))
