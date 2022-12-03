from itertools import starmap

from common import get_lines
from more_itertools import chunked

from .part1 import ITEM_VALUE


def find_common(rucksack: str, *others: str) -> str:
    items = set(rucksack)
    items.intersection_update(*others)
    assert len(items) == 1
    return items.pop()


def run() -> int:
    return sum(
        ITEM_VALUE[i]
        for i in starmap(
            find_common,
            chunked(get_lines(day=3), n=3),
        )
    )
