from ast import literal_eval
from dataclasses import dataclass
from itertools import groupby, zip_longest
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias

from common import fcast, read_lines

Data: TypeAlias = list["Data"] | int


@dataclass
class Packet:
    data: Data

    def __lt__(self, o: "Packet") -> bool:
        return bool(compare((self.data, o.data)))


def compare(pair: tuple[Data | None, Data | None]) -> bool | None:
    """
    >>> compare(([1,1,3,1,1], [1,1,5,1,1]))
    True
    >>> compare(([[1],[2,3,4]], [[1],4]))
    True
    >>> compare(([9], [[8,7,6]]))
    False
    >>> compare(([[4,4],4,4], [[4,4],4,4,4]))
    True
    >>> compare(([7,7,7,7], [7,7,7]))
    False
    >>> compare(([], [3]))
    True
    >>> compare(([[[]]], [[]]))
    False
    >>> compare(([1,[2,[3,[4,[5,6,7]]]],8,9], [1,[2,[3,[4,[5,6,0]]]],8,9]))
    False
    """
    match pair:
        case None, _:
            return True

        case _, None:
            return False

        case int() as left, int() as right:
            if left < right:
                return True
            if left > right:
                return False
            return None
        case list() as left, list() as right:
            for sub_pair in zip_longest(left, right):
                if (result := compare(sub_pair)) is None:
                    continue
                return result

            return None

        case int() as left, list() as right:
            return compare(([left], right))

        case list() as left, int() as right:
            return compare((left, [right]))

        case _:
            assert False


def parse(line: str) -> Data:
    return literal_eval(line)


def get_pairs(lines: Iterable[str]) -> Iterator[tuple[Data, Data]]:
    for group, lines in groupby(lines, key=bool):
        if not group:
            continue

        yield parse(next(lines)), parse(next(lines))


def get_packets(lines: Iterable[str]) -> Iterator[Packet]:
    for line in lines:
        if not line:
            continue
        yield Packet(parse(line))

    yield Packet([[2]])
    yield Packet([[6]])


def get_indices(pairs: Iterable[tuple[Data, Data]]) -> Iterator[int]:
    for i, pair in enumerate(pairs, 1):
        if compare(pair):
            yield i


def get_decoder_key(packets: list[Packet]) -> int:
    return (packets.index(Packet([[2]])) + 1) * (packets.index(Packet([[6]])) + 1)


@fcast(tuple)
def run(path: Path):
    yield sum(get_indices(get_pairs(read_lines(path))))
    yield get_decoder_key(sorted(get_packets(read_lines(path))))
