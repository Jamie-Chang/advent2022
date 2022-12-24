from __future__ import annotations
from collections import deque

from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cache, cached_property
from itertools import chain, count
from pathlib import Path
from typing import Generic, Iterable, Iterator, Self, TypeAlias, TypeVar, assert_never

from common import fcast, read_lines

T = TypeVar("T")
Coord: TypeAlias = tuple[int, int]


@dataclass
class SparseGrid(Generic[T]):
    data: dict[Coord, T] = field(default_factory=dict)

    def translate(self, key: Coord) -> Coord:
        rows, cols = self.dimensions
        row, col = key
        return rows[row], cols[col]

    @cached_property
    def dimensions(self) -> tuple[range, range]:
        return (
            range(min(r for r, _ in self.data), max(r for r, _ in self.data) + 1),
            range(min(c for _, c in self.data), max(c for _, c in self.data) + 1),
        )

    def __getitem__(self, key: Coord) -> T:
        return self.data[self.translate(key)]

    def __setitem__(self, key: Coord, value: T):
        self.data[self.translate(key)] = value

    def __contains__(self, key: Coord) -> bool:
        return key in self.data

    def items(self) -> Iterator[tuple[Coord, T]]:
        yield from self.data.items()

    def keys(self) -> Iterator[Coord]:
        rows, cols = self.dimensions
        for row in rows:
            for col in cols:
                yield row, col

    def rows(self) -> Iterator[Iterator[T]]:
        rows, cols = self.dimensions
        for row in rows:
            yield (self[row, col] for col in cols)


class Direction(Enum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"


class Tile(Enum):
    WALL = auto()
    PATH = auto()


Cell: TypeAlias = tuple[Tile, list[Direction]]


def parse_cell(s: str) -> Cell:
    if s == "#":
        return Tile.WALL, []

    if s == ".":
        return Tile.PATH, []

    if s == ">":
        return Tile.PATH, [Direction.RIGHT]

    if s == "<":
        return Tile.PATH, [Direction.LEFT]

    if s == "^":
        return Tile.PATH, [Direction.UP]

    if s == "v":
        return Tile.PATH, [Direction.DOWN]

    assert False


def move(coord: Coord, direction: Direction) -> Coord:
    row, col = coord
    match direction:
        case Direction.UP:
            return row - 1, col

        case Direction.DOWN:
            return row + 1, col

        case Direction.LEFT:
            return row, col - 1

        case Direction.RIGHT:
            return row, col + 1

        case key:
            assert_never(key)


@dataclass
class Valley:
    grid: SparseGrid[Cell]

    @property
    def start(self) -> Coord:
        return (0, 1)

    @property
    def finish(self) -> Coord:
        return self.grid.translate((-1, -2))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        data = {}

        for r, line in enumerate(lines):
            for c, cell in enumerate(line):
                data[r, c] = parse_cell(cell)
        return cls(SparseGrid(data))

    def display(self) -> str:
        def map_cell(cell: Cell):
            if cell[0] is Tile.WALL:
                return "#"

            if len(cell[1]) == 1:
                return cell[1][0].value

            if cell[1]:
                return str(len(cell[1]))

            return "."

        return "\n".join("".join(map_cell(c) for c in row) for row in self.grid.rows())

    def moves(self, coord: Coord) -> Iterator[Coord]:
        for direction in Direction:
            new_coord = move(coord, direction)
            rows, cols = self.grid.dimensions
            if new_coord[0] not in rows:
                continue

            if new_coord[1] not in cols:
                continue

            if self.grid[new_coord][0] is Tile.WALL:
                continue

            yield new_coord

    def move_blizzard(self, coord: Coord, direction: Direction) -> Coord:
        new_coord = move(coord, direction)
        if self.grid[new_coord][0] is Tile.PATH:
            return new_coord

        row, col = new_coord
        rows, cols = self.grid.dimensions
        match direction:
            case Direction.UP:
                return rows[-2], col

            case Direction.DOWN:
                return rows[1], col

            case Direction.LEFT:
                return row, cols[-2]

            case Direction.RIGHT:
                return row, cols[1]

            case key:
                assert_never(key)

    def next(self) -> Valley:
        data = {}

        for coord, (tile, blizzards) in self.grid.items():
            if coord not in data:
                data[coord] = tile, []

            if tile is Tile.WALL:
                continue

            for direction in blizzards:
                data.setdefault(
                    self.move_blizzard(coord, direction),
                    (
                        Tile.PATH,
                        [],
                    ),
                )[1].append(direction)

        return Valley(grid=SparseGrid(data))


def bfs(valleys: list[Valley], start: Coord, finish: Coord, time: int = 0) -> int:
    seen = set()
    queue: deque[tuple[Coord, int]] = deque([(start, time)])
    while queue:
        coord, time = queue.popleft()
        valley_id = time % len(valleys)
        if coord == finish:
            return time

        if valleys[valley_id].grid[coord][1]:
            continue

        if (coord, valley_id) in seen:
            continue

        seen.add((coord, valley_id))

        for move in chain(valleys[valley_id].moves(coord), [coord]):
            queue.append((move, time + 1))
    assert False


@fcast(tuple)
def run(data: Path):
    valleys = [Valley.from_lines(read_lines(data))]
    while True:
        valley = valleys[-1].next()
        if valley == valleys[0]:
            break

        valleys.append(valley)

    start = valleys[0].start
    finish = valleys[0].finish

    time = bfs(valleys, start, finish)
    yield time

    time = bfs(valleys, finish, start, time)
    yield bfs(valleys, start, finish, time)
