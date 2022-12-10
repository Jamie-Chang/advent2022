from itertools import islice
from pathlib import Path
from typing import Iterable, Iterator

from common import read_lines


def run_program(instructions: Iterable[str]) -> Iterator[int]:
    register = 1
    for instruction in instructions:
        tokens = instruction.split(" ")
        match tokens:
            case ["noop"]:
                yield register
            case ["addx", value]:
                yield register
                yield register
                register += int(value)


def get_signal_strength(values: Iterable[int]) -> Iterator[int]:
    for i, v in enumerate(values, 1):
        yield i * v


def get_pixel_value(sprite_positions: Iterable[int]) -> Iterator[str]:
    for p, sp in enumerate(sprite_positions):
        if abs(p % 40 - sp) <= 1:
            yield "#"
        else:
            yield " "


def get_screen_lines(pixel_values: Iterable[str]) -> Iterable[str]:
    pixels = iter(pixel_values)
    while True:
        line = "".join(islice(pixels, 40))
        if not line:
            break

        yield line


def run(path: Path):
    strength = sum(islice(get_signal_strength(run_program(read_lines(path))), 19, 220, 40))
    screen = "\n".join(get_screen_lines(get_pixel_value(run_program(read_lines(path)))))
    print(screen)
    return strength, screen
