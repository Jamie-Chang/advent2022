from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from itertools import cycle, groupby, islice, repeat, zip_longest
import math
from pathlib import Path
from typing import (
    Generic,
    Iterable,
    Iterator,
    Literal,
    Self,
    Sequence,
    TypeAlias,
    TypeVar,
    assert_never,
    overload,
)

from common import read_lines

T = TypeVar("T")

Coord: TypeAlias = tuple[int, int]


@dataclass
class Grid(Generic[T]):
    """
    >>> grid = Grid([[1, 2], [3, 4]])
    >>> grid[1, 1]
    4
    >>> grid[:, :]
    Grid(trees=[[1, 2], [3, 4]])
    >>> grid[::-1, ::-1]
    Grid(trees=[[4, 3], [2, 1]])
    >>> grid[::-1, 1]
    [4, 2]
    >>> grid[1, ::-1]
    [4, 3]
    """

    trees: list[list[T]]

    @overload
    def __getitem__(self, key: Coord) -> T:
        ...

    @overload
    def __getitem__(self, key: tuple[slice, int]) -> list[T]:
        ...

    @overload
    def __getitem__(self, key: tuple[int, slice]) -> list[T]:
        ...

    @overload
    def __getitem__(self, key: tuple[slice, slice]) -> Grid:
        ...

    def __getitem__(self, key):
        match key:
            case slice() as r, slice() as c:
                rows = self.trees[r]
                return Grid(list(map(lambda row: row[c], rows)))

            case slice() as r, int() as c:
                rows = self.trees[r]
                return list(map(lambda row: row[c], rows))

            case int() as r, slice() as c:
                row = self.trees[r]
                return row[c]

            case int() as r, int() as c:
                return self.trees[r][c]

            case key:
                assert_never(key)


class Tile(Enum):
    EMPTY = auto()
    OPEN = auto()
    WALL = auto()

    @classmethod
    def from_string(cls, string: str) -> Self:
        if string == ".":
            return cls.OPEN

        if string == "#":
            return cls.WALL

        return cls.EMPTY


class Direction(int, Enum):
    R = 0
    D = 1
    L = 2
    U = 3


def rotate_left(direction: Direction) -> Direction:
    match direction:
        case Direction.R:
            return Direction.U
        case Direction.D:
            return Direction.R
        case Direction.L:
            return Direction.D
        case Direction.U:
            return Direction.L
        case d:
            assert_never(d)


def rotate_right(direction: Direction) -> Direction:
    match direction:
        case Direction.R:
            return Direction.D
        case Direction.D:
            return Direction.L
        case Direction.L:
            return Direction.U
        case Direction.U:
            return Direction.R
        case d:
            assert_never(d)


def parse(lines: Iterable[str]) -> Grid[tuple[Coord, Tile]]:
    data = [
        [((r, c), Tile.from_string(v)) for c, v in enumerate(l)]
        for r, l in enumerate(lines)
    ]
    width = max(len(row) for row in data)
    for r, row in enumerate(data):
        for c in range(len(row), width):
            row.append(((r, c), Tile.EMPTY))

    return Grid(data)


def get_origin(grid: Grid) -> Coord:
    for position, value in grid[0, :]:
        if value is Tile.OPEN:
            return position
    assert False


def walk(grid: Grid, start: Coord, direction: Direction):
    after = lambda it: islice(it, 1, None)
    non_empty = lambda it: filter(lambda t: t[1] is not Tile.EMPTY, it)

    row, col = start
    match direction:
        case Direction.R:
            return after(cycle(non_empty(grid[row, col:] + grid[row, :col])))

        case Direction.D:
            return after(cycle(non_empty(grid[row:, col] + grid[:row, col])))

        case Direction.L:
            return after(cycle(non_empty(grid[row, col::-1] + grid[row, :col:-1])))

        case Direction.U:
            return after(cycle(non_empty(grid[row::-1, col] + grid[:row:-1, col])))

        case value:
            assert_never(value)


def parse_instructions(line: str) -> Iterator[int | str]:
    """
    >>> list(parse_instructions("10R15L5"))
    [10, 'R', 15, 'L', 5]
    """
    buffer = ""
    for current, lookahead in zip_longest(line, line[1:]):
        if current.isdigit():
            buffer += current

        else:
            yield current

        if buffer and not (lookahead and lookahead.isdigit()):
            yield int(buffer)
            buffer = ""


def run(data: Path):
    groups = (lines for k, lines in groupby(read_lines(data), key=bool) if k)
    grid = parse(next(groups))

    position = get_origin(grid)
    direction = Direction.R
    for instruction in parse_instructions(next(next(groups))):
        match instruction:
            case int() as number:
                for p, tile in islice(walk(grid, position, direction), number):
                    if tile is Tile.WALL:
                        break
                    position = p

            case "L":
                direction = rotate_left(direction)
            case "R":
                direction = rotate_right(direction)


    return (position[0] + 1) * 1000 + (position[1] + 1) * 4 + int(direction)
