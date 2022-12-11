from __future__ import annotations

import operator
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path
from typing import Callable, Generic, Iterable, Iterator, NewType, Self, TypeVar, cast

from parse import compile

from common import fcast, read_lines, strict

MonkeyNumber = NewType("MonkeyNumber", int)
T = TypeVar("T", int, "WorryLevel")


@dataclass
class Test(Generic[T]):
    divisor: int
    next_monkey: dict[bool, MonkeyNumber]

    def __call__(self, number: T) -> MonkeyNumber:
        return self.next_monkey[number % self.divisor == 0]


@dataclass
class Monkey(Generic[T]):
    number: MonkeyNumber
    operation: Callable[[T], T]
    test: Test
    items: list[T] = field(default_factory=list)
    inspected: int = 0


@dataclass(frozen=True)
class WorryLevel:
    remainders: tuple[tuple[int, int], ...]

    @classmethod
    def create(cls, level: int, divisible_by: list[int]) -> Self:
        return WorryLevel(tuple((d, level % d) for d in divisible_by))

    def __mul__(self, value: int | WorryLevel) -> WorryLevel:
        if isinstance(value, int):
            return WorryLevel(tuple((d, (r * value) % d) for d, r in self.remainders))

        return WorryLevel(tuple((d, (r * r) % d) for d, r in self.remainders))

    def __add__(self, value: int) -> WorryLevel:
        return WorryLevel(tuple((d, (r + value) % d) for d, r in self.remainders))

    def __mod__(self, value: int) -> int:
        return dict(self.remainders)[value]


monkey_line = strict(compile("Monkey {:d}:"))


def parse_monkey_number(line: str) -> MonkeyNumber:
    return MonkeyNumber(monkey_line.parse(line)[0])


def parse_starting_items(line: str) -> list[int]:
    items = line.removeprefix("  Starting items: ").split(", ")
    return [int(v) for v in items]


def parse_operator(op: str) -> Callable[[T | int, T | int], T]:
    match op:
        case "*":
            return operator.mul

        case "+":
            return operator.add

        case _:
            assert False


def parse_operation(line: str) -> Callable[[T], T]:
    """
    >>> parse_operation("  Operation: new = old * 7")(10)
    70
    >>> parse_operation("  Operation: new = old * old")(10)
    100
    """
    tokens = line.removeprefix("  Operation: new = ").split(" ")
    match tokens:
        case ["old", op, "old"]:
            return lambda w: parse_operator(op)(w, w)

        case ["old", op, other] | [other, op, "old"]:
            return lambda w: parse_operator(op)(w, int(other))

        case _:
            assert False


test_line = strict(compile("  Test: divisible by {:d}"))
true_line = strict(compile("    If true: throw to monkey {:d}"))
false_line = strict(compile("    If false: throw to monkey {:d}"))


def parse_test(lines: Iterable[str]) -> Test:
    """
    >>> lines = [
    ...     "  Test: divisible by 2",
    ...     "    If true: throw to monkey 7",
    ...     "    If false: throw to monkey 1",
    ... ]
    >>> test = parse_test(lines)
    >>> test(102)
    7
    >>> test(101)
    1

    """
    lines = iter(lines)
    divisor = test_line.parse(next(lines))[0]
    return Test(
        divisor,
        next_monkey={
            True: MonkeyNumber(true_line.parse(next(lines))[0]),
            False: MonkeyNumber(false_line.parse(next(lines))[0]),
        },
    )


def parse_monkey(lines: Iterable[str]) -> Monkey[int]:
    """
    >>> lines = [
    ...     "Monkey 0:",
    ...     "  Starting items: 62, 92, 50, 63, 62, 93, 73, 50",
    ...     "  Operation: new = old * 7",
    ...     "  Test: divisible by 2",
    ...     "    If true: throw to monkey 7",
    ...     "    If false: throw to monkey 1",
    ... ]
    >>> monkey, items = parse_monkey(lines)
    >>> monkey.number
    0
    >>> items
    [62, 92, 50, 63, 62, 93, 73, 50]
    >>> monkey.operation(62) == 62 * 7
    True
    """
    lines = iter(lines)
    return Monkey(
        number=parse_monkey_number(next(lines)),
        items=parse_starting_items(next(lines)),
        operation=parse_operation(next(lines)),
        test=parse_test(lines),
    )


def parse_inputs(lines: Iterable[str]) -> Iterator[Monkey]:
    for key, lines in groupby(lines, key=bool):
        if key is False:
            continue

        yield parse_monkey(lines)


def use_worry_levels(monkeys: Iterable[Monkey[int]]) -> Iterator[Monkey[WorryLevel]]:
    monkeys = list(monkeys)
    divisors = [m.test.divisor for m in monkeys]
    for monkey in monkeys:
        int_items = monkey.items
        monkey = cast(Monkey[WorryLevel], monkey)
        monkey.items = [WorryLevel.create(i, divisors) for i in int_items]
        yield monkey


def part1_round(monkeys: list[Monkey[int]]):
    for monkey in monkeys:
        new_worry_levels = (monkey.operation(w) // 3 for w in monkey.items)

        for w in new_worry_levels:
            new_monkey = monkey.test(w)
            monkeys[new_monkey].items.append(w)
            monkey.inspected += 1

        monkey.items.clear()


def part2_round(monkeys: list[Monkey[WorryLevel]]):
    for monkey in monkeys:
        new_worry_levels = (monkey.operation(w) for w in monkey.items)

        for w in new_worry_levels:
            new_monkey = monkey.test(w)
            monkeys[new_monkey].items.append(w)
            monkey.inspected += 1

        monkey.items.clear()


def get_monkey_business(monkeys: list[Monkey]) -> int:
    runner_up, first = sorted(m.inspected for m in monkeys)[-2:]
    return runner_up * first


@fcast(tuple)
def run(path: Path):
    monkeys = list(parse_inputs(read_lines(path)))
    for _ in range(20):
        part1_round(monkeys)

    yield get_monkey_business(monkeys)

    monkeys = list(use_worry_levels(parse_inputs(read_lines(path))))

    for _ in range(10_000):
        part2_round(monkeys)

    yield get_monkey_business(monkeys)
