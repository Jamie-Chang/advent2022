from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import combinations
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias

from parse import compile

from common import fcast, read_lines, strict

FORMAT = strict(
    compile("Valve {name} has flow rate={rate:d}; {:w} {:w} to {:w} {tunnels}")
)


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int
    tunnels: tuple[str, ...]


DistanceMatrix: TypeAlias = dict[Valve, dict[Valve, int]]


@dataclass
class Map:
    valves: dict[str, Valve]

    def __getitem__(self, name: str) -> Valve:
        return self.valves[name]

    def __iter__(self) -> Iterator[Valve]:
        yield from self.valves.values()

    def neighbours_of(self, valve: Valve) -> Iterator[Valve]:
        return (self.valves[t] for t in valve.tunnels)

    @cached_property
    def distance_matrix(self) -> DistanceMatrix:
        distance_matrix: DistanceMatrix = {}

        for valve in self.valves.values():
            for neighbour in self.neighbours_of(valve):
                distance_matrix.setdefault(valve, {})[neighbour] = 1

        while paths := list(discover_new_paths(distance_matrix)):
            for start, end, distance in paths:
                distance_matrix[start][end] = distance

        return distance_matrix

    def next_valves(
        self, valve: Valve, max_distance: int, ignore: frozenset[Valve]
    ) -> Iterator[tuple[Valve, int]]:
        for neighbour, distance in self.distance_matrix[valve].items():
            if neighbour.rate == 0:
                # No point going
                continue
            if distance > max_distance:
                continue

            if neighbour in ignore:
                continue

            yield neighbour, distance

    def max_flow(
        self,
        start: Valve,
        time: int = 30,
        open_valves: frozenset[Valve] = frozenset(),
        restrict: frozenset[Valve] | None = None,
    ) -> int:
        released = 0
        if start.rate > 0:
            # Needs to open
            open_valves = open_valves.union([start])
            time -= 1
            released += start.rate * time

        neighbours = self.next_valves(start, max_distance=time - 1, ignore=open_valves)

        return released + max(
            (
                (
                    self.max_flow(
                        n,
                        time=time - d,
                        open_valves=open_valves,
                        restrict=restrict,
                    )
                )
                for n, d in neighbours
                if not restrict or n in restrict
            ),
            default=0,
        )


def discover_new_paths(
    distance_matrix: DistanceMatrix,
) -> Iterable[tuple[Valve, Valve, int]]:
    for start, destinations in distance_matrix.items():
        for end, d1 in destinations.items():
            for next_end, d2 in distance_matrix[end].items():
                if next_end == start:
                    continue

                new_distance = d1 + d2
                old_distance = destinations.get(next_end)
                if old_distance and old_distance <= new_distance:
                    continue

                yield start, next_end, new_distance


def parse_valves(lines: Iterable[str]) -> Iterator[Valve]:
    """
    >>> valves = [
    ...     "Valve AA has flow rate=0; tunnels lead to valves DD, II, BB",
    ...     "Valve BB has flow rate=13; tunnels lead to valves CC, AA",
    ...     "Valve CC has flow rate=2; tunnels lead to valves DD, BB",
    ...     "Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE",
    ...     "Valve EE has flow rate=3; tunnels lead to valves FF, DD",
    ...     "Valve FF has flow rate=0; tunnels lead to valves EE, GG",
    ...     "Valve GG has flow rate=0; tunnels lead to valves FF, HH",
    ...     "Valve HH has flow rate=22; tunnel leads to valve GG",
    ...     "Valve II has flow rate=0; tunnels lead to valves AA, JJ",
    ...     "Valve JJ has flow rate=21; tunnel leads to valve II",
    ... ]
    >>> len(list(parse_valves(valves)))
    10
    """
    for line in lines:
        data = FORMAT.parse(line)
        yield Valve(data["name"], data["rate"], tuple(data["tunnels"].split(", ")))


def partitions(
    valves: frozenset[Valve],
) -> Iterator[tuple[frozenset[Valve], frozenset[Valve]]]:
    i = 0
    for n in range(1, len(valves) // 2 + 1):
        for group in combinations(valves, n):
            group = frozenset(group)
            yield group, valves - group
            i += 1


def releases(
    volcano: Map, partitions: Iterable[Iterable[frozenset[Valve]]]
) -> Iterator[int]:
    time = 26
    start = volcano["AA"]

    for groups in partitions:
        yield sum(volcano.max_flow(start, time, restrict=group) for group in groups)


@fcast(tuple)
def run(path: Path):

    volcano = Map({v.name: v for v in parse_valves(read_lines(path))})
    yield volcano.max_flow(volcano["AA"])
    yield max(
        releases(
            volcano,
            partitions(frozenset(v for v in volcano if v.rate > 0)),
        ),
    )
