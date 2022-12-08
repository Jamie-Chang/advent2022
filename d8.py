from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Iterable, Iterator, assert_never, overload

from common import read_lines


@dataclass
class Grid:
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

    trees: list[list[int]]

    @property
    def dimension(self) -> tuple[int, int]:
        return len(self.trees), len(self.trees[0])

    @overload
    def __getitem__(self, key: tuple[int, int]) -> int:
        ...

    @overload
    def __getitem__(self, key: tuple[slice, int]) -> list[int]:
        ...

    @overload
    def __getitem__(self, key: tuple[int, slice]) -> list[int]:
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


def visible_indices(trees: Iterable[int]) -> Iterator[int]:
    """
    >>> list(visible_indices([1, 1, 2, 4, 2]))
    [0, 2, 3]
    """
    current_max = -math.inf
    for i, tree in enumerate(trees):
        if tree <= current_max:
            # Blocked
            continue

        yield i
        current_max = tree


def get_visible(grid: Grid) -> Iterable[tuple[int, int]]:
    """
    >>> grid = Grid(
    ...     [
    ...         [3, 0, 3, 7, 3],
    ...         [2, 5, 5, 1, 2],
    ...         [6, 5, 3, 3, 2],
    ...         [3, 3, 5, 4, 9],
    ...         [3, 5, 3, 9, 0],
    ...     ]
    ... )
    >>> len(set(get_visible(grid)))
    21
    """
    height, width = grid.dimension

    # left -> right
    for row in range(height):
        yield from map(lambda c: (row, c), visible_indices(grid[row, :]))

    # right -> left
    for row in range(height):
        yield from map(lambda c: (row, width - 1 - c), visible_indices(grid[row, ::-1]))

    # top -> bottom
    for col in range(width):
        yield from map(lambda r: (r, col), visible_indices(grid[:, col]))

    # bottom -> top
    for col in range(width):
        yield from map(
            lambda r: (height - 1 - r, col), visible_indices(grid[::-1, col])
        )


def get_viewing_distance(height: int, trees: Iterable[int]) -> int:
    """
    >>> get_viewing_distance(5, [4, 9])
    2
    >>> get_viewing_distance(5, [3, 3])
    2
    >>> get_viewing_distance(5, [3, 5, 3])
    2
    >>> get_viewing_distance(5, [3])
    1
    """
    score = 0
    for h in trees:
        score += 1
        if h >= height:
            break

    return score


def product(values: Iterable[int]) -> int:
    start = 1
    for value in values:
        start *= value

    return start


def get_sides(grid: Grid, row: int, col: int) -> Iterator[list[int]]:
    """
    >>> grid = Grid(
    ...     [
    ...         [3, 0, 3, 7, 3],
    ...         [2, 5, 5, 1, 2],
    ...         [6, 5, 3, 3, 2],
    ...         [3, 3, 5, 4, 9],
    ...         [3, 5, 3, 9, 0],
    ...     ]
    ... )
    >>> expected = [
    ...     [3, 5, 3],
    ...     [3],
    ...     [3, 3],
    ...     [4, 9],
    ... ]
    >>> list(get_sides(grid, 3, 2)) == expected
    True
    """

    # up
    yield grid[row::-1, col][1:]
    # down
    yield grid[row:, col][1:]
    # left
    yield grid[row, col::-1][1:]
    # right
    yield grid[row, col:][1:]


def get_scenic_scores(grid: Grid) -> Iterator[int]:
    height, width = grid.dimension

    for row in range(height):
        for col in range(width):
            yield product(
                (
                    get_viewing_distance(grid[row, col], side)
                    for side in get_sides(grid, row, col)
                )
            )


def run(path: Path):
    grid = Grid(list(map(lambda r: list(map(int, r)), read_lines(path))))
    return len(set(get_visible(grid))), max(get_scenic_scores(grid))
