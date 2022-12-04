from typing import TypeAlias
from common import get_lines

from parse import compile


Assignment: TypeAlias = tuple[tuple[int, int], tuple[int, int]]


ASSIGNMENT_FORMAT = compile("{:d}-{:d},{:d}-{:d}")


def parse_assignment(line: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    >>> parse_assignment("30-60,47-87")
    ((30, 60), (47, 87))
    """
    result = ASSIGNMENT_FORMAT.parse(line)
    return tuple(result[:2]), tuple(result[2:])  # type: ignore


def overlaps(assignment: Assignment) -> bool:
    match assignment:
        case (s1, e1), (s2, e2) if s1 <= s2 and e1 >= e2:
            return True
        case (s1, e1), (s2, e2) if s1 >= s2 and e1 <= e2:
            return True
        case _:
            return False


def run():
    assignments = map(parse_assignment, get_lines(day=4))
    return sum(1 for assignment in assignments if overlaps(assignment))
