from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Iterator, ParamSpec, TypeVar, cast

from parse import Parser, Result


def get_input(*, day: int) -> Path:
    return Path(__file__).parent / "inputs" / f"d{day}.txt"


def read_lines(path: Path) -> Iterator[str]:
    with path.open() as f:
        for line in f:
            yield line.rstrip()


T1 = TypeVar("T1")
T2 = TypeVar("T2")
P = ParamSpec("P")


def fcast(caster: Callable[[T1], T2]) -> Callable[[Callable[P, T1]], Callable[P, T2]]:
    def wrapper(fn: Callable[P, T1]) -> Callable[P, T2]:
        @wraps(fn)
        def _fn(*args: P.args, **kwargs: P.kwargs) -> T2:
            return caster(fn(*args, **kwargs))

        return _fn

    return wrapper


@dataclass
class strict:
    parser: Parser

    def parse(self, string: str) -> Result:
        result = self.parser.parse(string)
        assert result is not None
        return cast(Result, result)
