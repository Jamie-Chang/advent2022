from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Iterator, NamedTuple, NewType, TypeAlias, cast

from more_itertools import chunked
from parse import compile

from common import strict

Crate = NewType("Crate", str)
StackNumber = NewType("StackNumber", int)

Stacks: TypeAlias = dict[StackNumber, "Stack"]


@dataclass
class Stack:
    stack: list[Crate] = field(default_factory=list)

    def push_many(self, crates: list[Crate]) -> None:
        self.stack.extend(crates)

    def push(self, crate: Crate) -> None:
        self.push_many([crate])

    def push_bottom(self, crate: Crate) -> None:
        self.stack.insert(0, crate)

    def pop_many(self, number: int) -> list[Crate]:
        remaining, result = self.stack[:-number], self.stack[-number:]
        self.stack = remaining
        return result

    def pop(self) -> Crate:
        return self.stack.pop()

    def peek(self) -> Crate:
        return self.stack[-1]


def parse_starting_stacks_line(line: str):
    for stack, crate in enumerate(chunked(line, 4), 1):
        if crate[1].isnumeric():
            return

        if crate[1] == " ":
            continue

        yield StackNumber(stack), Crate(crate[1])


def parse_starting_stacks(lines: Iterable[str]) -> dict[StackNumber, Stack]:
    stacks = defaultdict(Stack)
    for line in lines:
        if not line:
            break

        for stack, crate in parse_starting_stacks_line(line):
            stacks[stack].push_bottom(crate)

    return stacks


class Move(NamedTuple):
    number: int
    start: StackNumber
    end: StackNumber


LINE_FORMAT = strict(compile("move {number:d} from {start:d} to {end:d}"))


def parse_move(line: str) -> Move:
    result = LINE_FORMAT.parse(line)
    return Move(
        result["number"],
        StackNumber(result["start"]),
        StackNumber(result["end"]),
    )


def parse(lines: Iterable[str]) -> tuple[Stacks, Iterator[Move]]:
    lines = iter(lines)
    return parse_starting_stacks(lines), (parse_move(l) for l in lines)


def read_answer(stacks: Stacks) -> str:
    return "".join(stacks[StackNumber(s)].peek() for s in range(1, max(stacks) + 1))


def run(lines: Iterable[str]):
    stacks, moves = parse(lines)
    for number, start, end in moves:
        for _ in range(number):
            stacks[end].push(stacks[start].pop())

    return read_answer(stacks)
