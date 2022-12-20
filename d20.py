from __future__ import annotations

from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Iterable, Self

from common import fcast, nth, read_lines


@dataclass
class Link:
    """
    >>> link = create_links([0, 1, 2, 3, 4])[0]
    >>> link.to_list(5)
    [0, 1, 2, 3, 4]
    >>> link.move(2)
    >>> link.to_list(5)
    [0, 3, 4, 1, 2]
    >>> link.move(-2)
    >>> link.to_list(5)
    [0, 1, 2, 3, 4]
    >>> link.move(7)
    >>> link.to_list(5)
    [0, 3, 4, 1, 2]
    >>> link.move(-7)
    >>> link.to_list(5)
    [0, 1, 2, 3, 4]
    >>> link.move(0)
    >>> link.to_list(5)
    [0, 1, 2, 3, 4]
    """

    value: int
    _backwards: Link | None = None
    _forwards: Link | None = None

    @property
    def backwards(self) -> Link:
        assert self._backwards
        return self._backwards

    @backwards.setter
    def backwards(self, value: Link):
        self._backwards = value
        value._forwards = self

    @property
    def forwards(self) -> Link:
        assert self._forwards
        return self._forwards

    @forwards.setter
    def forwards(self, value: Link):
        self._forwards = value
        value._backwards = self

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
        link_before = self
        if amount == 0:
            return

        if amount >= 0:
            link_before = nth(self, amount)
            link_after = link_before.forwards
        else:
            link_after = nth(reversed(self), abs(amount))
            link_before = link_after.backwards

        # Remove self
        self.backwards.forwards = self.forwards

        # Relink self
        self.forwards = link_after
        self.backwards = link_before


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
            link = links[-1].forwards = Link(v)
            links.append(link)

        links[-1].forwards = links[0]

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
