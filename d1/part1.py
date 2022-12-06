import itertools
from typing import Iterable, Iterator


def get_snacks(lines: Iterable[str]) -> Iterator[Iterator[int]]:
    return (map(int, g) for k, g in itertools.groupby(lines, key=bool) if k)


def run(lines: Iterable[str]):
    return max(map(sum, get_snacks(lines)))
