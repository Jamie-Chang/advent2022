from pathlib import Path
from typing import Iterator


def get_lines(*, day: int) -> Iterator[str]:
    path = Path(f"d{day}") / "input.txt"
    with path.open() as f:
        for line in f:
            yield line.rstrip()
