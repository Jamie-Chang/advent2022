from typing import Iterable

from .part1 import parse, read_answer


def run(lines: Iterable[str]):
    stacks, moves = parse(lines)
    for number, start, end in moves:
        stacks[end].push_many(stacks[start].pop_many(number))

    return read_answer(stacks)
