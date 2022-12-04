from common import get_lines

from .part1 import Assignment, parse_assignment



def overlaps(assignment: Assignment) -> bool:
    """
    >>> overlaps(parse_assignment("5-7,7-9"))
    True
    >>> overlaps(parse_assignment("2-8,3-7"))
    True
    >>> overlaps(parse_assignment("6-6,4-6"))
    True
    >>> overlaps(parse_assignment("2-6,4-8"))
    True
    >>> overlaps(parse_assignment("2-4,6-8"))
    False
    >>> overlaps(parse_assignment("2-3,4-5"))
    False
    """
    match assignment:
        case (s1, e1), (s2, e2) if s1 > e2:
            return False

        case (s1, e1), (s2, e2) if e1 < s2:
            return False

        case _:
            return True


def run() -> int:
    assignments = map(parse_assignment, get_lines(day=4))
    return sum(1 for assignment in assignments if overlaps(assignment))
