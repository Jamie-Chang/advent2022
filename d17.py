from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle
from pathlib import Path
from typing import Hashable, Iterable, Iterator, NamedTuple, Self, Sequence, TypeVar

from common import fcast, nth


@dataclass(frozen=True)
class Coord:
    row: int
    col: int

    def __iter__(self) -> Iterator[int]:
        yield self.row
        yield self.col

    def __add__(self, other: Coord) -> Coord:
        return Coord(
            self.row + other.row,
            self.col + other.col,
        )

    def __sub__(self, other: Coord) -> Coord:
        return Coord(
            self.row - other.row,
            self.col - other.col,
        )

    def __neg__(self) -> Coord:
        return Coord(
            -self.row,
            -self.col,
        )


LEFT = Coord(0, -1)
RIGHT = Coord(0, 1)
UP = Coord(1, 0)
DOWN = Coord(-1, 0)


def read_string(lines: Sequence[str]) -> Iterator[Coord]:
    for r, line in enumerate(reversed(lines)):
        for c, pixel in enumerate(line):
            if pixel == "#":
                yield Coord(r, c)


@dataclass
class Shape:
    """
    Lines of pixels sparsely stored.

    Coordinates are upside down for convenience.

    >>> lines = ['####']
    >>> list(Shape.from_string(lines).to_string()) == lines
    True
    """

    pixels: set[Coord] = field(default_factory=set)
    origin: Coord = Coord(0, 0)
    dimensions: tuple[int, int] = (0, 0)

    @classmethod
    def from_coords(cls, coords: Iterable[Coord]) -> Self:
        shape = cls()
        for coord in coords:
            shape.add(coord)
        return shape

    @classmethod
    def from_string(cls, lines: list[str]) -> Self:
        coords = set(read_string(lines))
        return cls(
            coords,
            dimensions=(
                max(p.row for p in coords) + 1,
                max(p.col for p in coords) + 1,
            ),
        )

    def __contains__(self, coord: Coord) -> bool:
        return coord in self.pixels

    def add(self, pixel: Coord) -> None:
        row, col = pixel
        height, width = self.dimensions
        self.dimensions = max(row + 1, height), max(col + 1, width)
        self.pixels.add(pixel)

    def to_string(self) -> Iterator[str]:
        height, width = self.dimensions
        row, col = self.origin
        for r in range(row, row + height)[::-1]:
            # print([Coord(r, c) for c in range(col, col + width)])
            yield "".join(
                "#" if Coord(r, c) in self.pixels else "."
                for c in range(col, col + width)
            )

    def move(self, delta: Coord) -> None:
        self.origin += delta
        self.pixels = {pixel + delta for pixel in self.pixels}

    def transpose(self, to: Coord) -> None:
        self.move(to - self.origin)

    def isdisjoint(self, other: Shape) -> bool:
        return self.pixels.isdisjoint(other.pixels)

    def __delitem__(self, rows: slice) -> None:
        row_range = range(-1, self.dimensions[0])[rows]
        self.pixels = {pixel for pixel in self.pixels if pixel.row not in row_range}

    def __ior__(self, other: Shape) -> Shape:
        for pixel in other.pixels:
            self.add(pixel)

        return self


def get_rocks() -> Iterator[Shape]:
    yield Shape.from_string(
        [
            "####",
        ]
    )
    yield Shape.from_string(
        [
            ".#.",
            "###",
            ".#.",
        ]
    )
    yield Shape.from_string(
        [
            "..#",
            "..#",
            "###",
        ]
    )
    yield Shape.from_string(
        [
            "#",
            "#",
            "#",
            "#",
        ]
    )
    yield Shape.from_string(
        [
            "##",
            "##",
        ]
    )


def get_directions(directions: str) -> Iterator[Coord]:
    for direction in directions:
        if direction == ">":
            yield RIGHT
        if direction == "<":
            yield LEFT


def in_bound(rock: Shape):
    return (
        rock.origin.col + rock.dimensions[1] <= 7
        and rock.origin.col >= 0
        and rock.origin.row >= 0
    )


def try_move(chamber: Shape, rock: Shape, direction: Coord):
    rock.move(direction)
    if not in_bound(rock):
        rock.move(-direction)
        return False

    if not chamber.isdisjoint(rock):
        rock.move(-direction)
        return False

    return True


STEPS = [RIGHT, UP, LEFT, DOWN]
DIAGONAL_STEPS = [RIGHT + UP, RIGHT + DOWN, LEFT + UP, LEFT + DOWN]


def normalise(outline: tuple[Coord, ...]) -> tuple[Coord, ...]:
    delta = -outline[0]
    return tuple(coord + delta for coord in outline)


def get_lower_outline(chamber: Shape) -> tuple[Coord, ...]:
    top_left = max(
        (pixel for pixel in chamber.pixels if pixel.col == 0), key=lambda c: c.row
    )
    seen = set()
    queue: list[tuple[Coord, ...]] = [(top_left,)]
    while queue:
        path = queue.pop(0)
        if path[-1].col == 6:
            return path

        for move in STEPS + DIAGONAL_STEPS:
            new_position = path[-1] + move
            if new_position in seen:
                continue
            seen.add(new_position)
            if new_position not in chamber:
                continue
            if all(new_position + d in chamber for d in [RIGHT, DOWN, LEFT, UP]):
                continue

            queue.append((*path, new_position))

    assert False


class State(NamedTuple):
    rock_cycle: int
    direction_cycle: int
    outline: tuple[Coord, ...]


def get_chamber_state(
    rocks: Iterable[tuple[int, Shape]],
    directions: Iterable[tuple[int, Coord]],
) -> Iterator[tuple[State, int]]:
    chamber = Shape.from_coords(Coord(-1, c) for c in range(7))
    direction_state = 0

    for rock_state, rock in rocks:
        rock.transpose(Coord(chamber.dimensions[0] + 3, 2))
        for direction_state, direction in directions:
            try_move(chamber, rock, direction)

            if try_move(chamber, rock, DOWN):
                continue

            chamber |= rock
            outline = normalise(get_lower_outline(chamber))
            cycle_state = State(rock_state, direction_state, outline)
            yield cycle_state, chamber.dimensions[0]
            break


T_STATE = TypeVar("T_STATE", bound=Hashable)


@dataclass
class CumulativeCycle:
    """
    >>> cycle = CumulativeCycle([0, 0, 1, 2, 3, 4], start=2)
    >>> cycle[0]
    0
    >>> cycle[2]
    1
    >>> cycle[5]
    4
    >>> cycle.size
    3
    >>> cycle.cumulation
    3
    >>> cycle[6]
    5
    """

    values: list[int]
    start: int

    @property
    def size(self) -> int:
        return len(self.values) - self.start - 1

    @property
    def cumulation(self) -> int:
        return self.values[-1] - self.values[self.start]

    def __getitem__(self, index: int) -> int:
        if index < self.start:
            return self.values[index]

        cycles = (index - self.start) // self.size
        remainder = self.values[(index - self.start) % self.size + self.start]
        return cycles * self.cumulation + remainder

    @classmethod
    def from_iterable(cls, values: Iterator[tuple[T_STATE, int]]) -> Self:
        heights: list[int] = []
        state_index_map: dict[T_STATE, int] = {}
        for i, (state, value) in enumerate(values):
            heights.append(value)
            if state in state_index_map:
                return CumulativeCycle(heights, start=state_index_map[state])

            state_index_map[state] = i

        assert False


@fcast(tuple)
def run(path: Path):
    rocks = cycle(enumerate(get_rocks()))
    directions = cycle(enumerate(get_directions(path.read_text())))
    _, height = nth(get_chamber_state(rocks, directions), n=2021)
    yield height

    rocks = cycle(enumerate(get_rocks()))
    directions = cycle(enumerate(get_directions(path.read_text())))
    yield CumulativeCycle.from_iterable(
        get_chamber_state(
            rocks,
            directions,
        )
    )[1000000000000 - 1]
