from pathlib import Path
from typing import Iterator


def get_path(*, day: int) -> Path:
    return Path(f"d{day}") / "input.txt"


def get_lines(*, day: int) -> Iterator[str]:
    with get_path(day=day).open() as f:
        for line in f:
            yield line.rstrip()
