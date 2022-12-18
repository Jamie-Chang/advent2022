from collections import deque
from dataclasses import dataclass
import operator
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias


from common import fcast, isum, read_lines


Coord: TypeAlias = tuple[int, int, int]


def get_cubes(lines: Iterable[str]) -> Iterator[Coord]:
    """
    >>> list(get_cubes(["2,2,2"]))
    [(2, 2, 2)]
    """

    for line in lines:
        yield tuple(map(int, line.split(",")))


def get_neighbours(coord: Coord, diagonal: bool = False) -> Iterator[Coord]:
    """
    >>> neighbours = set(get_neighbours((0, 0, 0)))
    >>> neighbours == {
    ...     (1, 0, 0),
    ...     (-1, 0, 0),
    ...     (0, 1, 0),
    ...     (0, -1, 0),
    ...     (0, 0, 1),
    ...     (0, 0, -1),
    ... }
    True
    """

    x, y, z = coord
    yield x + 1, y, z
    yield x - 1, y, z
    yield x, y + 1, z
    yield x, y - 1, z
    yield x, y, z + 1
    yield x, y, z - 1

    if not diagonal:
        return

    yield x + 1, y + 1, z
    yield x - 1, y + 1, z
    yield x - 1, y - 1, z
    yield x + 1, y - 1, z

    yield x + 1, y, z + 1
    yield x - 1, y, z + 1
    yield x - 1, y, z - 1
    yield x + 1, y, z - 1

    yield x, y + 1, z + 1
    yield x, y + 1, z - 1
    yield x, y - 1, z - 1
    yield x, y - 1, z + 1


def get_surface_area(cubes: set[Coord]) -> Iterator[int]:
    for cube in cubes:
        yield sum(1 for n in get_neighbours(cube) if n not in cubes)


def distance_squared(cube: Coord, start: Coord = (0, 0, 0)) -> int:
    """
    >>> distance_squared((1, 1, 1))
    3
    """
    return sum(diff * diff for diff in map(operator.sub, cube, start))


@dataclass
class Droplet:
    """
    >>> sum(1 for _ in Droplet(cubes={(0, 0, 0), (0, 0, 1), }).get_outer_surface())
    10
    """

    cubes: set[Coord]

    def get_starting_point(self) -> Coord:

        assert self.cubes
        # Get cube with minimal distance
        starting_cube = min(self.cubes, key=lambda c: c[0])
        return starting_cube[0] - 1, starting_cube[1], starting_cube[2]

    def get_outer_surface_area(self) -> int:
        return sum(isum(surfaces) for _, surfaces in self._get_air_shell())

    def _get_air_shell(self) -> Iterator[tuple[Coord, Iterator[Coord]]]:
        start = self.get_starting_point()
        visited: set[Coord] = set()
        queue = deque([start])
        while queue:
            coord = queue.popleft()
            if coord in visited:
                continue
            visited.add(coord)

            if not any(n in self.cubes for n in get_neighbours(coord, diagonal=True)):
                continue

            neighbours = list(get_neighbours(coord))

            yield coord, (n for n in neighbours if n in self.cubes)
            queue.extend(n for n in neighbours if n not in self.cubes)


@fcast(tuple)
def run(data: Path):
    cubes = set(get_cubes(read_lines(data)))

    yield sum(get_surface_area(cubes))
    yield Droplet(cubes).get_outer_surface_area()
