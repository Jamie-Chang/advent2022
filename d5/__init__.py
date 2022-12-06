from pathlib import Path

from common import read_lines

from . import part1, part2


def run(path: Path):
    return part1.run(read_lines(path)), part2.run(read_lines(path))
