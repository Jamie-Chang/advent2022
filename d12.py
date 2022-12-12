import string
from collections import deque
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable, Iterator, Self, TypeAlias

from common import read_lines

Coord: TypeAlias = tuple[int, int]

HEIGHT_MAP = {l: i for i, l in enumerate(string.ascii_lowercase)}


@dataclass
class Search:
    search: Iterable[tuple[Coord, int]]
    reached: dict[Coord, int]

    def __iter__(self):
        return iter(self.search)


@dataclass
class Grid:
    """
    >>> grid = Grid.from_lines(
    ...     [
    ...         "abcd",
    ...         "Sbcd",
    ...         "abcE",
    ...         "abcd",
    ...     ]
    ... )
    >>> grid.start
    (1, 0)
    >>> grid.end
    (2, 3)
    >>> list(grid.neighbours((1, 0)))
    [(2, 0), (0, 0), (1, 1)]
    """

    grid: list[list[int]]
    start: Coord
    end: Coord

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        start = None
        end = None
        rows = []
        for row, line in enumerate(lines):
            cols = []
            for col, letter in enumerate(line):
                if letter == "S":
                    start = row, col
                    letter = "a"
                if letter == "E":
                    end = row, col
                    letter = "z"
                cols.append(HEIGHT_MAP[letter])
            rows.append(cols)
        assert start and end
        return cls(rows, start, end)

    @cached_property
    def dimensions(self) -> tuple[int, int]:
        return len(self.grid), len(self.grid[0])

    def __getitem__(self, coord: Coord) -> int:
        return self.grid[coord[0]][coord[1]]

    def _search(self, start: Coord, reached: dict[Coord, int], backwards: bool = False):
        queue: deque[tuple[Coord, int]] = deque([(start, 0)])
        while queue:
            coord, distance = queue.popleft()
            if coord in reached:
                continue
            reached[coord] = distance

            yield coord, distance

            queue.extend((n, distance + 1) for n in self.neighbours(coord, backwards))

    def search(self, start: Coord, backwards: bool = False) -> Search:
        reached = {}
        return Search(self._search(start, reached, backwards), reached)

    def valid_coords(self, coords: Iterable[Coord]) -> Iterator[Coord]:
        row, col = self.dimensions
        for r, c in coords:
            if 0 <= r < row and 0 <= c < col:
                yield r, c

    def _neighbours(self, coord: Coord) -> Iterator[Coord]:
        row, col = coord
        yield row + 1, col
        yield row - 1, col
        yield row, col + 1
        yield row, col - 1

    def neighbours(self, coord: Coord, backwards: bool = False) -> Iterator[Coord]:
        neighbour_coords = self.valid_coords(self._neighbours(coord))
        current_height = self[coord]
        for neighbour in neighbour_coords:
            delta = self[neighbour] - current_height
            if backwards:
                delta = -delta

            if delta <= 1:
                yield neighbour


def part1(grid: Grid) -> int:
    forward = grid.search(grid.start)
    backward = grid.search(grid.end, backwards=True)
    for f, b in zip(forward, backward):
        if f[0] in backward.reached:
            return backward.reached[f[0]] + f[1]

        if b[0] in forward.reached:
            return forward.reached[b[0]] + b[1]

    assert False


def part2(grid: Grid) -> int:
    for coord, distance in grid.search(grid.end, backwards=True):
        if grid[coord] == 0:
            return distance

    assert False


def run(path: Path):
    grid = Grid.from_lines(read_lines(path))
    return part1(grid), part2(grid)
