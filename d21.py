from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Callable, Iterable, Self, cast

from common import read_lines


@dataclass
class Monkey:
    monkeys: dict[str, Monkey]
    number: Decimal | str | None = None

    @property
    def result(self) -> Decimal:
        assert self.number is not None
        if isinstance(self.number, Decimal):
            return self.number

        left, op, right = self.number.split(" ")

        left_value = self.monkeys[left].result
        right_value = self.monkeys[right].result

        if op == "*":
            return left_value * right_value

        if op == "+":
            return left_value + right_value

        if op == "-":
            return left_value - right_value

        if op == "/":
            return left_value / right_value

        assert False


@dataclass
class Monkeys:
    monkeys: dict[str, Monkey] = field(default_factory=dict)

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        monkeys = cls()
        for line in lines:
            monkeys.add(*parse_line(line))

        return monkeys

    def add(self, name: str, number: str | Decimal) -> Monkey:
        monkey = self.monkeys[name] = Monkey(self.monkeys, number)
        return monkey

    def pop(self, name: str) -> Monkey:
        return self.monkeys.pop(name)

    def __getitem__(self, name: str) -> Monkey:
        return self.monkeys[name]


def parse_line(line: str) -> tuple[str, Decimal | str]:
    name, number = line.split(": ")
    if number.isdigit():
        return name, Decimal(number)

    return name, number


def newton_raphson(
    fn: Callable[[Decimal], Decimal],
    start: Decimal = Decimal(0),
    target: Decimal = Decimal(0),
) -> Decimal:
    while True:
        start_val = fn(start)
        gradient = (fn(start + 1) - start_val) // 1
        diff = target - start_val
        if diff == 0:
            return start
        start += diff // gradient


def difference(number: Decimal, human: Monkey, root: Monkey):
    human.number = number
    return root.result


def part1(lines: Iterable[str]) -> Decimal:
    return Monkeys.from_lines(lines)["root"].result


def part2(lines: Iterable[str]) -> Decimal:
    monkeys = Monkeys.from_lines(lines)

    root = monkeys["root"]
    human = monkeys["humn"]

    left, _, right = cast(str, root.number).split(" ")
    root.number = f"{left} - {right}"

    return newton_raphson(lambda n: difference(n, human, root))


def run(data: Path):
    return int(part1(read_lines(data))), int(part2(read_lines(data)))
