from heapq import nlargest

from .part1 import get_lines, get_snacks


def run():
    return sum(nlargest(3, map(sum, get_snacks(get_lines()))))
