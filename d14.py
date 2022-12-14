from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, Iterator, NewType, TypeAlias, TypeVar

from common import fcast, read_lines

Right = NewType("Depth", int)
Down = NewType("Depth", int)


Coord: TypeAlias = tuple[Right, Down]


class Tile(Enum):
    AIR = auto()
    ROCK = auto()
    SAND = auto()


@dataclass
class Grid:
    data: dict[Coord, Tile]
    floor: Down | None = None
    _max_depth: Down = field(init=False)

    def __post_init__(self):
        self._max_depth = max(coord[1] for coord in self.data)

    @property
    def max_depth(self):
        if self.floor:
            return self.floor

        return self._max_depth

    def __getitem__(self, coord: Coord) -> Tile:
        if self.floor and coord[1] == self.floor:
            return Tile.ROCK

        if coord not in self.data:
            return Tile.AIR

        return self.data[coord]

    def __setitem__(self, coord: Coord, value: Tile):
        if value is Tile.AIR:
            self.data.pop(coord, None)

        self.data[coord] = value

    def next_coord(self, coord: Coord) -> Coord | None:
        right, down = coord

        neighbours = [
            (Right(right), Down(down + 1)),
            (Right(right - 1), Down(down + 1)),
            (Right(right + 1), Down(down + 1)),
        ]
        for n in neighbours:
            if self[n] is Tile.AIR:
                return n
        return None

    def fall_from(self, start: Coord) -> Coord | None:
        if self[start] is not Tile.AIR:
            return None

        coord = start
        while new_coord := self.next_coord(coord):
            if new_coord[1] > self.max_depth:
                return None

            coord = new_coord

        return coord


def parse_coord(string: str) -> Coord:
    """
    >>> parse_coord("499,23")
    (499, 23)
    """
    r, d = map(int, string.split(","))
    return Right(r), Down(d)


T = TypeVar("T")


def window(items: Iterable[T], n: int) -> Iterator[list[T]]:
    last = []
    for item in items:
        last.append(item)
        if len(last) == n:
            yield last
            last = last[1:]


def parse_line(line: str) -> Iterator[Coord]:
    path = (parse_coord(c) for c in line.split(" -> "))
    for start, finish in window(path, n=2):
        match start, finish:
            case (x1, y1), (x2, y2) if x1 == x2:
                for y in range(y1, y2, max(-1, min(1, (y2 - y1)))):
                    yield x1, Down(y)

            case (x1, y1), (x2, y2) if y1 == y2:
                for x in range(x1, x2, max(-1, min(1, (x2 - x1)))):
                    yield Right(x), y1

        yield finish


def parse(lines: Iterable[str]) -> Grid:
    data = {}
    for line in lines:
        for coord in parse_line(line):
            data[coord] = Tile.ROCK

    return Grid(data)


def fill(grid: Grid, start: Coord) -> Iterator[Coord]:
    while position := grid.fall_from(start):
        grid[position] = Tile.SAND
        yield position


@fcast(tuple)
def run(path: Path):
    start = (Right(500), Down(0))
    grid = parse(read_lines(path))
    yield (units := sum(1 for _ in fill(grid, start)))

    grid.floor = Down(grid.max_depth + 2)
    yield units + sum(1 for _ in fill(grid, start))
