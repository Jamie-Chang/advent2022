import string
from typing import Iterable, Iterator
from common import get_lines

letters = string.ascii_lowercase + string.ascii_uppercase
ITEM_VALUE = {letter: value for value, letter in enumerate(letters, 1)}


def get_compartments(lines: Iterable[str]) -> Iterator[tuple[str, str]]:
    for line in lines:
        yield line[: len(line) // 2], line[len(line) // 2 :]


def find_item(compartments: tuple[str, str]) -> str:
    """
    >>> find_item(("abcd", "defg"))
    'd'
    """

    value = set(compartments[0]) & set(compartments[1])
    return value.pop()


def run():

    items = map(find_item, get_compartments(get_lines(day=3)))
    return sum(ITEM_VALUE[item] for item in items)
