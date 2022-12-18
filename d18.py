from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple, TypeAlias

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


class Surface(NamedTuple):
    """
    The surface is the boundary between the two coordinates.
    """

    air: Coord
    cube: Coord


@dataclass
class Droplet:
    """
    >>> isum(Droplet(cubes={(0, 0, 0), (0, 0, 1)}).get_outer_surface())
    10
    """

    cubes: set[Coord]

    def get_starting_point(self) -> Coord:

        assert self.cubes
        # Get cube with minimal distance
        starting_cube = min(self.cubes, key=lambda c: c[0])
        return starting_cube[0] - 1, starting_cube[1], starting_cube[2]

    def get_surface(self) -> Iterator[Surface]:
        for cube in self.cubes:
            for neighbour in get_neighbours(cube):
                if neighbour not in self.cubes:
                    yield Surface(neighbour, cube)

    def get_outer_surface(self) -> Iterator[Surface]:
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
            for neighbour in neighbours:
                if neighbour in self.cubes:
                    yield Surface(air=coord, cube=neighbour)
                else:
                    queue.append(neighbour)


@fcast(tuple)
def run(data: Path):
    droplet = Droplet(set(get_cubes(read_lines(data))))

    yield isum(droplet.get_surface())
    yield isum(droplet.get_outer_surface())
