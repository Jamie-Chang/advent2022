from heapq import nlargest

from common import get_lines

from .part1 import get_lines, get_snacks


def run():
    return sum(nlargest(3, map(sum, get_snacks(get_lines(day=1)))))
