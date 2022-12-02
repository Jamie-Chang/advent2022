from __future__ import annotations

from enum import Enum, auto
from typing import Iterable, Iterator

from common import get_lines


class Result(Enum):
    LOSE = auto()
    DRAW = auto()
    WIN = auto()


class Action(Enum):
    ROCK = auto()
    PAPER = auto()
    SCISSOR = auto()


WINS_AGAINST = {
    Action.ROCK: Action.SCISSOR,
    Action.PAPER: Action.ROCK,
    Action.SCISSOR: Action.PAPER,
}
LOSE_AGAINST = {v: k for k, v in WINS_AGAINST.items()}


PLAYER_MAP = {
    "X": Action.ROCK,
    "Y": Action.PAPER,
    "Z": Action.SCISSOR,
}

OPPONENT_MAP = {
    "A": Action.ROCK,
    "B": Action.PAPER,
    "C": Action.SCISSOR,
}


RESULT_SCORE = {
    Result.WIN: 6,
    Result.DRAW: 3,
    Result.LOSE: 0,
}

ACTION_SCORE = {
    Action.ROCK: 1,
    Action.PAPER: 2,
    Action.SCISSOR: 3,
}


def get_result(opponent: Action, player: Action) -> Result:
    if WINS_AGAINST[player] is opponent:
        return Result.WIN

    if LOSE_AGAINST[player] is opponent:
        return Result.LOSE

    return Result.DRAW


def get_strategy(
    lines: Iterable[str],
) -> Iterator[tuple[Action, Action]]:
    for line in lines:
        opponent, player = line.split(" ")
        yield OPPONENT_MAP[opponent], PLAYER_MAP[player]


def score(strategy: Iterator[tuple[Action, Action]]) -> int:
    return sum(RESULT_SCORE[get_result(o, p)] + ACTION_SCORE[p] for o, p in strategy)


def run() -> int:
    return score(get_strategy(get_lines(day=2)))
