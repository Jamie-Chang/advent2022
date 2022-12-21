from __future__ import annotations

from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Iterable, Self

from common import fcast, nth, read_lines


@dataclass
class Link:
    value: int
    backwards: Link = field(init=False)
    forwards: Link = field(init=False)

    def __post_init__(self):
        self.backwards = self.forwards = self

    def append(self, link: Link) -> None:
        self.forwards.backwards = link.backwards
        link.backwards.forwards = self.forwards

        self.forwards = link
        link.backwards = self

    def prepend(self, link: Link) -> None:
        link.forwards.backwards = self.backwards
        self.backwards.forwards = link.forwards

        link.forwards = self
        self.backwards = link

    def unlink(self) -> None:
        self.forwards.backwards = self.backwards
        self.backwards.forwards = self.forwards
        self.forwards = self
        self.backwards = self

    def __iter__(self):
        value = self
        while True:
            yield value
            value = value.forwards

    def __reversed__(self):
        value = self
        while True:
            yield value
            value = value.backwards

    def move(self, amount: int):

        if amount > 0:
            link_before = nth(self, amount)
            self.unlink()
            link_before.append(self)

        elif amount < 0:
            link_after = nth(reversed(self), abs(amount))
            self.unlink()
            link_after.prepend(self)


@dataclass
class CircularList:
    """
    >>> links = CircularList.from_values([0, 1, 2, 3])
    >>> links.origin.value
    0
    >>> links[0]
    0
    >>> links[1]
    1
    >>> links[-1]
    3
    >>> links
    CircularList([0, 1, 2, 3])
    >>> list(links)
    [0, 1, 2, 3]
    """

    links: list[Link]
    origin: Link = field(init=False)

    def __post_init__(self):
        for link in self.links:
            if link.value == 0:
                self.origin = link
                return

        assert False

    def __repr__(self) -> str:
        return f"CircularList({list(self)})"

    @classmethod
    def from_values(cls, values: Iterable[int]) -> Self:
        values = iter(values)
        links = [Link(next(values))]

        for v in values:
            link = Link(v)
            links[-1].append(link)
            links.append(link)

        return cls(links)

    def __iter__(self):
        return (link.value for link in islice(self.origin, len(self.links)))

    def __getitem__(self, value: int) -> int:
        value = normalise(value, len(self.links))
        if value < 0:
            return nth(reversed(self.origin), -value).value

        return nth(self.origin, value).value

    def __imul__(self, value: int) -> Self:
        for link in self.links:
            link.value *= value
        return self

    def mix(self):
        for link in self.links:
            movements = normalise(link.value, len(self.links) - 1)
            link.move(movements)

    @property
    def coordinates(self) -> tuple[int, int, int]:
        return tuple(self[i] for i in (1000, 2000, 3000))


def normalise(movement: int, length: int) -> int:
    """
    >>> normalise(-10, 7)
    -3
    >>> normalise(10, 7)
    3
    >>> normalise(-4744, 5000)
    256
    """
    movement %= length
    return min(movement, movement - length, key=abs)


@fcast(tuple)
def run(data: Path):
    values = CircularList.from_values(map(int, read_lines(data)))
    values.mix()
    yield sum(values.coordinates)

    values = CircularList.from_values(map(int, read_lines(data)))
    values *= 811589153
    for _ in range(10):
        values.mix()
    yield sum(values.coordinates)
