from common import get_path

from typing import Iterable, Iterator, TypeVar


T = TypeVar("T")


def window(it: Iterable[T], size: int) -> Iterator[list[T]]:
    """
    >>> list(window('abcd', 2))
    [['a', 'b'], ['b', 'c'], ['c', 'd']]
    """
    buffer = []
    for elem in it:
        buffer.append(elem)

        if len(buffer) == size:
            yield buffer
            buffer = buffer[1:]


def unique(it: Iterable) -> bool:
    seen = set()
    for i in it:
        if i in seen:
            return False
        seen.add(i)

    return True


def first(it: Iterable[T]) -> T:
    return next(iter(it))


def get_marker_position(stream: str, size: int):
    marker_window = window(stream, size)
    return first(p for p, w in enumerate(marker_window, size) if unique(w))


def run():
    stream = get_path(day=6).read_text()
    return get_marker_position(stream, 4), get_marker_position(stream, 14)
