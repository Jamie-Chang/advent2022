from common import get_lines

from .part1 import parse, read_answer


def run():
    stacks, moves = parse(get_lines(day=5))
    for number, start, end in moves:
        stacks[end].push_many(stacks[start].pop_many(number))

    return read_answer(stacks)
