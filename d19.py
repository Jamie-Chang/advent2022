from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from itertools import islice
from math import ceil
from pathlib import Path
from typing import Iterable, Iterator, Self

from parse import compile

from common import fcast, read_lines, strict

FORMAT = strict(
    compile(
        "Blueprint {id:d}: "
        "Each ore robot costs {ore[ore]:d} ore. "
        "Each clay robot costs {clay[ore]:d} ore. "
        "Each obsidian robot costs {obsidian[ore]:d} ore and {obsidian[clay]:d} clay. "
        "Each geode robot costs {geode[ore]:d} ore and {geode[obsidian]:d} obsidian."
    )
)


@dataclass
class Robot:
    resource: str
    cost: Counter[str]


@dataclass
class BluePrint:
    id: int
    robots: dict[str, Robot]

    @classmethod
    def from_string(cls, line: str) -> Self:
        """
        >>> actual = BluePrint.from_string(
        ...     "Blueprint 1: Each ore robot costs 4 ore. "
        ...     "Each clay robot costs 4 ore. "
        ...     "Each obsidian robot costs 4 ore and 18 clay. "
        ...     "Each geode robot costs 4 ore and 9 obsidian."
        ... )
        >>> expected = BluePrint(
        ...     1,
        ...     {
        ...         "ore": Robot("ore", Counter({"ore": 4})),
        ...         "clay": Robot("clay", Counter({"ore": 4})),
        ...         "obsidian": Robot("obsidian", Counter({"ore": 4, "clay": 18})),
        ...         "geode": Robot("geode", Counter({"ore": 4, "obsidian": 9})),
        ...     }
        ... )
        >>> actual == expected
        True
        """
        data = FORMAT.parse(line).named
        return cls(
            id=data.pop("id"),
            robots={
                resource: Robot(
                    resource,
                    Counter(cost),
                )
                for resource, cost in data.items()
            },
        )


def turns(to_gather: Counter[str], rate: Counter[str]) -> int:
    if not to_gather:
        return 0
    return max(ceil(v / rate[k]) for k, v in to_gather.items())


def multiply(resources: Counter[str], n: int) -> Counter[str]:
    return Counter({k: c * n for k, c in resources.items()})


@dataclass(frozen=True)
class State:
    time: int
    resources: Counter[str] = field(default_factory=Counter)
    production: Counter[str] = field(default_factory=Counter)

    def tick(self, time: int = 1) -> State:
        return State(
            time=self.time - time,
            resources=self.resources + multiply(self.production, time),
            production=self.production,
        )

    def wait_time(self, robot: Robot) -> int | None:
        if set(robot.cost.elements()) - set(self.production.elements()):
            return None

        return turns(robot.cost - self.resources, self.production)

    def buildable(self, blueprint: BluePrint) -> Iterator[Robot]:
        priority = ["geode", "ore", "clay", "obsidian"]
        for resource in priority:
            robot = blueprint.robots[resource]

            wait_time = self.wait_time(robot)

            if wait_time is None:
                continue

            if wait_time > self.time - 1 - 1:
                # takes wait time + 1 minute to build
                # takes another minute to produce
                continue

            if wait_time == 0 and resource == "geode":
                yield robot
                break

            resource_costs = (r.cost[resource] for r in blueprint.robots.values())

            if not any(c > self.production[resource] for c in resource_costs):
                # No point
                if resource != "geode":
                    continue

            yield robot

    def build(self, robot: Robot) -> State:
        t = turns(robot.cost - self.resources, self.production) + 1
        return State(
            time=self.time - t,
            resources=self.resources + multiply(self.production, t) - robot.cost,
            production=self.production + Counter([robot.resource]),
        )


def get_all_states(blueprint: BluePrint, time: int):
    print(f"{blueprint.id}")
    queue = deque([State(time, production=Counter(["ore"]))])

    while queue:
        state = queue.popleft()

        for robot in state.buildable(blueprint):
            queue.append(state.build(robot))

        yield state.tick(state.time)


def max_geodes(states: Iterable[State]) -> int:
    return max(state.resources["geode"] for state in states)


def product(iterable: Iterable[int]) -> int:
    start = 1
    for i in iterable:
        start *= i

    return start


@fcast(tuple)
def run(data: Path):
    blueprints = map(BluePrint.from_string, read_lines(data))
    yield sum(b.id * max_geodes(get_all_states(b, 24)) for b in blueprints)

    blueprints = islice(map(BluePrint.from_string, read_lines(data)), 3)
    yield product(max_geodes(get_all_states(b, 32)) for b in blueprints)
