from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

from common import read_lines


@dataclass
class File:
    size: int


@dataclass
class Directory:
    files: dict[str, File] = field(default_factory=dict)
    directories: dict[str, Directory] = field(default_factory=dict)


def get_tree(lines: Iterable[str]) -> Directory:
    """
    >>> tree = get_tree(
    ...     [
    ...         "$ cd /",
    ...         "$ ls",
    ...         "dir a",
    ...         "1 b.txt",
    ...         "2 c.dat",
    ...         "$ cd a",
    ...         "$ ls",
    ...         "5 d.dat",
    ...     ]
    ... )
    >>> tree == Directory(
    ...     {"b.txt": File(1), "c.dat": File(2)},
    ...     directories={"a": Directory(files={"d.dat": File(5)})},
    ... )
    True
    """
    root = Directory()

    stack: list[Directory] = []
    listing: bool = False

    for line in lines:
        tokens = line.split(" ")
        match tokens:
            case ["$", "cd", "/"]:
                listing = False
                stack = [root]

            case ["$", "cd", ".."]:
                listing = False
                stack.pop(-1)

            case ["$", "cd", child_directory]:
                listing = False
                child = stack[-1].directories[child_directory]
                stack.append(child)

            case ["$", "ls"]:
                listing = True

            case ["dir", child_directory]:
                assert listing
                stack[-1].directories[child_directory] = Directory()

            case [size, child_file]:
                assert listing
                stack[-1].files[child_file] = File(int(size))

    return root


def get_sizes(tree: Directory) -> Iterator[int]:
    """
    Get all sizes of directories.

    Includes any child directories (direct or otherwise)
    Last size element is the current directory size.

    >>> list(
    ...     get_sizes(
    ...         Directory(
    ...             {"b.txt": File(1), "c.txt": File(2)},
    ...             {"a": Directory({"d.txt": File(3)})},
    ...         )
    ...     )
    ... )
    [3, 6]
    """
    size = sum(f.size for f in tree.files.values())
    for child in tree.directories.values():
        last_size = 0
        for s in get_sizes(child):
            yield s
            last_size = s

        size += last_size

    yield size


def run(path: Path):
    root = get_tree(read_lines(path))
    sizes = list(get_sizes(root))
    root_size = sizes[-1]
    minimum = root_size - 40_000_000
    return sum(s for s in sizes if s <= 100000), min(s for s in sizes if s > minimum)
