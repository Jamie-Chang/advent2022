from pathlib import Path
from typing import Iterator


def get_input(*, day: int) -> Path:
    return Path(__file__).parent  / "inputs" / f"d{day}.txt"


def read_lines(path: Path) -> Iterator[str]:
    with path.open() as f:
        for line in f:
            yield line.rstrip()
