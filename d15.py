from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple, Self, TypeAlias

import parse

from common import fcast, first, read_lines, strict

Coord: TypeAlias = tuple[int, int]


class Sensor(NamedTuple):
    location: Coord
    beacon: Coord

    _format = strict(
        parse.compile("Sensor at x={:d}, y={:d}: closest beacon is at x={:d}, y={:d}")
    )

    @classmethod
    def from_string(cls, string: str) -> Self:
        """
        >>> Sensor.from_string("Sensor at x=2, y=18: closest beacon is at x=-2, y=15")
        Sensor(location=(2, 18), beacon=(-2, 15))
        """
        result = cls._format.parse(string)
        return cls((result[0], result[1]), (result[2], result[3]))


def manhattan_distance(start: Coord, end: Coord) -> int:
    return abs(start[0] - end[0]) + abs(start[1] - end[1])


def get_x_range(sensor: Sensor, y: int) -> range:
    delta_x = manhattan_distance(*sensor) - abs(sensor.location[1] - y)
    if delta_x < 0:
        return range(0, 0)
    return range(sensor.location[0] - delta_x, sensor.location[0] + delta_x + 1)


def filter_empty(fn):
    @functools.wraps(fn)
    def _fn(*args, **kwargs):
        for r in fn(*args, **kwargs):
            if not r:
                continue
            yield r

    return _fn


def range_intersect(a: range, b: range):
    assert a.step == b.step

    return range(max(a.start, b.start), min(a.stop, b.stop), a.step)


def range_join(a: range, b: range):
    assert a.step == b.step

    return range(min(a.start, b.start), max(a.stop, b.stop), a.step)


@filter_empty
def range_difference(a: range, b: range):
    assert a.step == b.step
    if len(range_intersect(a, b)) == 0:
        yield a
        return

    yield range(a.start, b.start)
    yield range(b.stop, a.stop)


@dataclass
class DisjointRange:
    ranges: list[range] = field(default_factory=list)

    def __and__(self, other: range | DisjointRange) -> DisjointRange:
        if isinstance(other, range):
            other = DisjointRange([other])

        ranges = []
        for r in self.ranges:
            for orange in other.ranges:
                r = range_intersect(r, orange)

            if r:
                ranges.append(r)
        return DisjointRange(ranges)

    def __sub__(self, other: range | DisjointRange) -> DisjointRange:
        if isinstance(other, range):
            other = DisjointRange([other])

        ranges = self.ranges
        for orange in other.ranges:
            new_ranges = []
            for r in ranges:
                new_ranges.extend(range_difference(r, orange))
            ranges = new_ranges
        return DisjointRange(ranges)

    def __or__(self, other: range | DisjointRange) -> DisjointRange:
        """
        >>> len(DisjointRange() | range(1))
        1
        """
        if isinstance(other, range):
            other = DisjointRange([other])

        ranges = self.ranges
        for new_range in other.ranges:
            new_ranges = []
            for r in ranges:
                if range_intersect(r, new_range):
                    new_range = range_join(r, new_range)

                else:
                    new_ranges.append(r)

            if new_range:
                new_ranges.append(new_range)

            ranges = new_ranges
        return DisjointRange(ranges)

    def __len__(self) -> int:
        return sum(map(len, self.ranges))

    def __iter__(self) -> Iterator[int]:
        for r in self.ranges:
            yield from r

    def __bool__(self) -> bool:
        return bool(self.ranges)


def possible_locations(
    sensors: list[Sensor], x_bound: range, y_bound: range
) -> Iterable[Coord]:
    for y in y_bound:
        x_values = DisjointRange([x_bound])
        for sensor in sensors:
            x_values -= get_x_range(sensor, y)

        for x in x_values:
            yield x, y


def unique(i: Iterable) -> int:
    return len(set(i))


@fcast(tuple)
def run(path: Path):
    sensors = list(map(Sensor.from_string, read_lines(path)))

    # Part 1
    target_y = 2000000
    excluded = DisjointRange()
    for sensor in sensors:
        excluded |= get_x_range(sensor, target_y)

    yield (
        len(excluded)
        - sum(1 for (_, y), _ in sensors if y == target_y)
        - unique(x for _, (x, y) in sensors if y == target_y)
    )

    # part 2
    bound = 4000000
    x, y = first(possible_locations(sensors, range(bound), range(bound)))
    yield x * bound + y
