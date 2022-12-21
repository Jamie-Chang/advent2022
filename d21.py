from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable, Iterable, Self, cast

from common import read_lines


@dataclass
class Monkey:
    monkeys: dict[str, Monkey]
    number: asyncio.Future[int | str] = field(
        init=False, default_factory=asyncio.Future
    )

    async def get_number(self) -> int | str:
        return await self.number

    def reset_number(self) -> None:
        self.number = asyncio.Future()

    def set_number(self, number: int | str) -> None:
        self.number.set_result(number)

    @property
    async def result(self) -> int:
        number = await self.number

        if isinstance(number, int):
            return number

        left, op, right = number.split(" ")
        left_value = await self.monkeys[left].result
        right_value = await self.monkeys[right].result

        if op == "*":
            return left_value * right_value

        if op == "+":
            return left_value + right_value

        if op == "-":
            return left_value - right_value

        if op == "/":
            return left_value // right_value

        assert False


@dataclass
class Monkeys:
    monkeys: dict[str, Monkey] = field(default_factory=dict)

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        monkeys = cls()
        for line in lines:
            name, number = parse_line(line)
            monkeys.add(name).set_number(number)
        return monkeys

    def add(self, name: str) -> Monkey:
        monkey = self.monkeys[name] = Monkey(self.monkeys)
        return monkey

    def pop(self, name: str) -> Monkey:
        return self.monkeys.pop(name)

    def __getitem__(self, name: str) -> Monkey:
        return self.monkeys[name]


def parse_line(line: str) -> tuple[str, int | str]:
    name, number = line.split(": ")
    if number.isdigit():
        return name, int(number)

    return name, number


async def newton_raphson(
    fn: Callable[[int], Awaitable[int]],
    start: int = 0,
    target: int = 0,
    delta: int = 3,
) -> int:
    while True:
        start_val = await fn(start)
        gradient = (await fn(start + delta) - start_val) // delta
        diff = target - start_val
        if diff == 0:
            return start
        start += diff // gradient


async def difference(number: int, human: Monkey, left: Monkey, right: Monkey):
    human.reset_number()
    human.set_number(number)
    value = await left.result - await right.result
    return value


async def part1(lines: Iterable[str]) -> int:
    monkeys = Monkeys.from_lines(lines)
    return await monkeys["root"].result


async def part2(lines: Iterable[str]) -> int:
    monkeys = Monkeys.from_lines(lines)

    root_formula = cast(str, await monkeys.pop("root").get_number())
    left, _, right = root_formula.split(" ")

    return await newton_raphson(
        lambda n: difference(
            n,
            monkeys["humn"],
            monkeys[left],
            monkeys[right],
        )
    )


def run(data: Path):
    return asyncio.run(part1(read_lines(data))), asyncio.run(part2(read_lines(data)))
