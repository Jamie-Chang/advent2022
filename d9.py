import itertools
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias, TypeVar

from common import read_lines


class Direction(Enum):
    U = auto()
    D = auto()
    L = auto()
    R = auto()


Position: TypeAlias = tuple[int, int]
Motion: TypeAlias = tuple[Direction, int]
Moves: TypeAlias = Iterator[Position]


def parse(line: str) -> tuple[Direction, int]:
    direction, steps = line.split()
    return Direction[direction], int(steps)


def move_head(position: Position, direction: Direction) -> Position:
    match direction:
        case Direction.U:
            return position[0], position[1] + 1
        case Direction.D:
            return position[0], position[1] - 1
        case Direction.L:
            return position[0] - 1, position[1]
        case Direction.R:
            return position[0] + 1, position[1]


def head_moves(motions: Iterable[Motion]) -> Moves:
    position = (0, 0)
    for direction, steps in motions:
        for _ in range(steps):
            yield (position := move_head(position, direction))


def move_tail(head: Position, tail: Position) -> Position:
    """
    >>> tail = (0, 0)
    >>> move_tail((0, 0), tail) == tail
    True
    >>> move_tail((1, 0), tail) == tail
    True
    >>> move_tail((0, 1), tail) == tail
    True
    >>> move_tail((-1, 0), tail) == tail
    True
    >>> move_tail((0, -1), tail) == tail
    True
    >>> move_tail((1, 1), tail) == tail
    True
    >>> move_tail((-1, 1), tail) == tail
    True
    >>> move_tail((1, -1), tail) == tail
    True
    >>> move_tail((-1, -1), tail) == tail
    True
    >>> move_tail((2, 0), tail)
    (1, 0)
    >>> move_tail((0, 2), tail)
    (0, 1)
    >>> move_tail((-2, 0), tail)
    (-1, 0)
    >>> move_tail((0, -2), tail)
    (0, -1)
    """
    match head, tail:
        case (hx, hy), (tx, ty) if abs(hx - tx) <= 1 and abs(hy - ty) <= 1:
            # touching
            return tail

        case (hx, hy), (tx, ty) if hx > tx and hy > ty:
            # Top Right
            return tx + 1, ty + 1

        case (hx, hy), (tx, ty) if hx < tx and hy > ty:
            # Top Left
            return tx - 1, ty + 1

        case (hx, hy), (tx, ty) if hx > tx and hy < ty:
            # Bottom Right
            return tx + 1, ty - 1

        case (hx, hy), (tx, ty) if hx < tx and hy < ty:
            # Bottom Left
            return tx - 1, ty - 1

        case (hx, hy), (tx, ty) if hx > tx and hy == ty:
            # Right
            return tx + 1, ty

        case (hx, hy), (tx, ty) if hx < tx and hy == ty:
            # Left
            return tx - 1, ty

        case (hx, hy), (tx, ty) if hx == tx and hy > ty:
            # Up
            return hx, ty + 1

        case (hx, hy), (tx, ty) if hx == tx and hy < ty:
            # Down
            return hx, ty - 1

        case _:
            return tail


def tail_of(head: Moves) -> Moves:
    yield (position := (0, 0))

    for p in head:
        yield (position := move_tail(p, position))


def knots(head: Moves) -> Iterator[Moves]:
    """Positions for all infinite possible knots.

    Each knots position is also an infinite iterator.
    """
    last_knot, head = itertools.tee(iter(head))
    yield repeat_end(head)
    while True:
        position, last_knot = itertools.tee(tail_of(last_knot), 2)
        yield repeat_end(position)


def rope(head: Moves, length: int) -> Iterator[tuple[Position, ...]]:
    return zip(*itertools.islice(knots(head), length))


T = TypeVar("T")


def repeat_end(iterable: Iterator[T]) -> Iterator[T]:
    v = unused = object()
    for v in iterable:
        yield v

    if v is unused:
        raise ValueError("Cannot repeat empty iterable")

    yield from itertools.repeat(v)  # type: ignore


def takewhile_change(iterable: Iterator[T]) -> Iterator[T]:
    last = object()
    for item in iterable:
        if item == last:
            return

        yield item
        last = item


def run(path: Path):
    motions = map(parse, read_lines(path))
    first = set()
    last = set()
    for r in takewhile_change(rope(head_moves(motions), 10)):
        first.add(r[1])
        last.add(r[9])

    return len(first), len(last)
