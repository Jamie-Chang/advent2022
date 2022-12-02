from typing import Iterable, Iterator

from common import get_lines

from .part1 import (
    ACTION_SCORE,
    LOSE_AGAINST,
    RESULT_SCORE,
    WINS_AGAINST,
    Action,
    Result,
    get_lines,
)


def get_action(opponent: Action, result: Result) -> Action:
    """
    >>> get_action(Action.ROCK, Result.WIN)
    <Action.PAPER: 2>
    """

    if result is result.LOSE:
        return WINS_AGAINST[opponent]

    if result is result.WIN:
        return LOSE_AGAINST[opponent]

    return opponent


RESULT_MAP = {
    "X": Result.LOSE,
    "Y": Result.DRAW,
    "Z": Result.WIN,
}

ACTION_MAP = {
    "A": Action.ROCK,
    "B": Action.PAPER,
    "C": Action.SCISSOR,
}


def get_strategy(lines: Iterable[str]) -> Iterator[tuple[Action, Result]]:
    for line in lines:
        opponent, result = line.split(" ")
        yield ACTION_MAP[opponent], RESULT_MAP[result]


def run() -> int:
    return sum(
        (ACTION_SCORE[get_action(o, r)] + RESULT_SCORE[r])
        for o, r in get_strategy(get_lines(day=2))
    )
