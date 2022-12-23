from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Iterable, Iterator, Literal, Self, TypeAlias, TypeVar

from common import fcast, first, read_lines

Coord: TypeAlias = tuple[int, int]

T = TypeVar("T")


def rotate(values: list[T], n: int = 1) -> list[T]:
    n %= len(values)
    return values[n:] + values[:n]


@dataclass
class Elf:
    state: Literal[0, 1, 2, 3] = 0

    def next_move(self, current: Coord, grid: Grid) -> Coord | None:
        changes = (-1, 0, 1)
        row, col = current
        values = rotate(
            [
                ((row - 1, col), any((row - 1, col + c) in grid for c in changes)),
                ((row + 1, col), any((row + 1, col + c) in grid for c in changes)),
                ((row, col - 1), any((row + c, col - 1) in grid for c in changes)),
                ((row, col + 1), any((row + c, col + 1) in grid for c in changes)),
            ],
            self.state,
        )
        self.state = (self.state + 1) % 4

        if not any(blocked for _, blocked in values):
            return None

        if all(blocked for _, blocked in values):
            return None

        return first(position for position, blocked in values if not blocked)


@dataclass
class Grid:
    positions: dict[Coord, Elf]

    def display(self) -> str:
        return "\n".join(
            "".join(("#" if (row, col) in self else ".") for col in self.col_range)
            for row in self.row_range
        )

    @property
    def row_range(self) -> range:
        return range(
            min(r for r, _ in self.positions),
            max(r for r, _ in self.positions) + 1,
        )

    @property
    def col_range(self) -> range:
        return range(
            min(c for _, c in self.positions),
            max(c for _, c in self.positions) + 1,
        )

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        positions = {}
        for row, line in enumerate(lines):
            for col, value in enumerate(line):
                if value == "#":
                    positions[row, col] = Elf()

        return cls(positions)

    @property
    def empty_space(self) -> int:
        return len(self.row_range) * len(self.col_range) - len(self.positions)

    def __contains__(self, position: Coord) -> bool:
        return position in self.positions

    def move(self, moves: Iterable[tuple[Coord, Coord]]) -> None:
        for start, finish in moves:
            self.positions[finish] = self.positions.pop(start)

    def get_moves(self) -> Iterator[tuple[Coord, Coord]]:
        next_positions: dict[Coord, list[tuple[Coord, Elf]]] = {}
        for position, elf in self.positions.items():
            next_position = elf.next_move(position, self)
            if next_position is None:
                continue

            next_positions.setdefault(next_position, []).append((position, elf))

        for next_position, elves in next_positions.items():
            if len(elves) > 1:
                continue

            yield elves[0][0], next_position


@fcast(tuple)
def run(data: Path):
    grid = Grid.from_lines(read_lines(data))
    for _ in range(10):
        grid.move(grid.get_moves())
    yield grid.empty_space

    move = 0
    for move in count(1):
        moves = list(grid.get_moves())
        if not moves:
            break

        grid.move(moves)

    yield move + 10
