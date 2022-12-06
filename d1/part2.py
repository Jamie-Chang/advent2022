from heapq import nlargest
from typing import Iterable

from .part1 import get_snacks


def run(lines: Iterable[str]) -> int:
    return sum(nlargest(3, map(sum, get_snacks(lines))))
