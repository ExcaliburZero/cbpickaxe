from dataclasses import dataclass
from typing import Dict, IO, List, Optional

import argparse
import enum
import json
import re
import sys

import intervaltree

SUCCESS = 0

NOON = 12
MIDNIGHT = 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--monster_spawn_profiles", nargs="+", required=True)
    parser.add_argument("--species_file", required=True)

    args = parser.parse_args(argv)

    with open(args.species_file, "r", encoding="utf8") as input_stream:
        species_ids = SpeciesInfo.read_ids(input_stream)

    for spawn_filepath in args.monster_spawn_profiles:
        with open(spawn_filepath, "r") as input_stream:
            monster_spawn_profile = MonsterSpawnProfile.from_tres(input_stream)

        print(monster_spawn_profile)

        spawn_rates = monster_spawn_profile.calculate_spawn_rates()
        print(spawn_rates)

        print("==============================")
        # print(monster_spawn_profile.habitat_name)
        print(spawn_filepath)
        for spawn_type in [SpawnType.Overworld, SpawnType.Backup]:
            rates = spawn_rates[spawn_type]

            if spawn_type == SpawnType.Overworld:
                print("{{OverworldMonstersTable")
            else:
                print("{{BackupMonstersTable")

            for i, rate in enumerate(
                sorted(
                    rates.rates, key=lambda r: species_ids[format_name(r.monster_form)]
                )
            ):
                i += 1
                print(f"| monster_{i} = {format_name(rate.monster_form)}")
                if spawn_type == SpawnType.Overworld:
                    world_monster = rate.world_monster
                    assert world_monster is not None
                    print(f"| monster_{i}_overworld = {format_name(world_monster)}")
                print(f"| monster_{i}_rate_day = {format_rate(rate.rates[Time.Day])}")
                print(
                    f"| monster_{i}_rate_night = {format_rate(rate.rates[Time.Night])}"
                )

            print("}}")
            print("-----")

    return SUCCESS


def format_name(name: str) -> str:
    parts = name.replace("_", " ").title().split("-")
    if len(parts) == 1:
        return parts[0]

    return parts[0] + "-" + str(parts[1][0]).lower() + str(parts[1][1:])


def format_rate(value: float) -> str:
    if 0.0000001 < value < 0.01:
        return "{{tt|" + f"{value:.1f}|{value}" + " %}}"

    return f"{value:.1f}"


class SpeciesInfo:
    @staticmethod
    def read_ids(input_stream: IO[str]) -> Dict[str, int]:
        data = json.load(input_stream)

        return {entry["name"]: entry["bestiary_index"] for entry in data}


@dataclass
class MonsterSpawnConfig:
    monster_form: str
    world_monster: Optional[str]
    weight: float
    hour_min: float
    hour_max: float

    def covers(self, time: int) -> bool:
        if self.hour_min > self.hour_max:
            return (0.0 <= time <= self.hour_max) or (self.hour_min <= time <= 24.0)

        return self.hour_min <= time <= self.hour_max

    @staticmethod
    def from_lines(
        lines: List[str], i: int, external_resources: "ExternalResources"
    ) -> "MonsterSpawnConfig":
        monster_form = (
            TresParser.get_value_resource(
                f"species_{i}/monster_form", external_resources, lines
            )
            .path.split("/")[-1]
            .split(".tres")[0]
        )

        world_monster = None
        try:
            world_monster = (
                TresParser.get_value_resource(
                    f"species_{i}/world_monster", external_resources, lines
                )
                .path.split("/")[-1]
                .split(".tscn")[0]
            )
        except ValueError:
            pass

        weight = float(TresParser.get_value(f"species_{i}/weight", lines))
        hour_min = float(TresParser.get_value(f"species_{i}/hour_min", lines))
        hour_max = float(TresParser.get_value(f"species_{i}/hour_max", lines))

        return MonsterSpawnConfig(
            monster_form, world_monster, weight, hour_min, hour_max
        )


class SpawnType(enum.Enum):
    Overworld = enum.auto()
    Backup = enum.auto()


class Time(enum.Enum):
    Day = enum.auto()
    Night = enum.auto()


@dataclass
class SpawnRate:
    monster_form: str
    world_monster: Optional[str]
    rates: Dict[Time, float]


@dataclass
class SpawnRates:
    rates: List[SpawnRate]


@dataclass
class MonsterSpawnProfile:
    habitat_name: str
    min_team_size: int
    max_team_size: int
    configs: List[MonsterSpawnConfig]

    def calculate_spawn_rates(
        self,
    ) -> Dict[SpawnType, SpawnRates]:
        return {
            spawn_type: self.__calculate_spawn_rates_of_type(spawn_type)
            for spawn_type in [SpawnType.Overworld, SpawnType.Backup]
        }

    def __calculate_spawn_rates_of_type(self, spawn_type: SpawnType) -> SpawnRates:
        interval_tree = intervaltree.IntervalTree()
        configs = [
            config
            for config in self.configs
            if spawn_type == SpawnType.Backup or config.world_monster is not None
        ]

        for config in configs:
            if config.hour_min > config.hour_max:
                interval_tree.addi(config.hour_min, 24.0, config)
                interval_tree.addi(0.0, config.hour_max, config)
            else:
                interval_tree.addi(config.hour_min, config.hour_max, config)

        day_total_weight = sum(
            (interval.data.weight for interval in interval_tree.at(NOON))
        )
        night_total_weight = sum(
            (interval.data.weight for interval in interval_tree.at(MIDNIGHT))
        )

        rates = []
        for config in configs:
            rates.append(
                SpawnRate(
                    config.monster_form,
                    config.world_monster,
                    rates={
                        Time.Day: (config.weight / day_total_weight) * 100.0
                        if config.covers(NOON)
                        else 0.0,
                        Time.Night: (config.weight / night_total_weight) * 100.0
                        if config.covers(MIDNIGHT)
                        else 0.0,
                    },
                )
            )

        return SpawnRates(rates)

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "MonsterSpawnProfile":
        # This is implemented in a dumb way to save on development time. There are definitely much
        # faster implementations possible.
        lines = [line for line in input_stream]

        external_resources = ExternalResources.from_lines(lines)

        habitat_name = (
            TresParser.get_value("habitat_name", lines)
            .strip()[1:-1]
            .replace("REGION_NAME_", "")
        )
        num_species = int(TresParser.get_value("num_species", lines))
        min_team_size = int(TresParser.get_value("min_team_size", lines))
        max_team_size = int(TresParser.get_value("max_team_size", lines))

        configs = [
            MonsterSpawnConfig.from_lines(lines, i, external_resources)
            for i in range(0, num_species)
        ]

        return MonsterSpawnProfile(habitat_name, min_team_size, max_team_size, configs)


@dataclass
class Resource:
    path: str
    type: str


@dataclass
class ExternalResources:
    resources: Dict[int, Resource]

    @staticmethod
    def from_lines(lines: List[str]) -> "ExternalResources":
        resources = {}
        for line in lines:
            if line.startswith("[ext_resource "):
                parts = re.search('path="(.*)" type="(.*)" id=(\d+)', line)

                assert parts is not None

                path = parts.group(1)
                type = parts.group(2)
                i = int(parts.group(3))

                resources[i] = Resource(path, type)

        return ExternalResources(resources)


class TresParser:
    @staticmethod
    def get_value(name: str, lines: List[str]) -> str:
        for line in lines:
            if line.startswith(f"{name} = "):
                return line[len(f"{name} = ") :]

        raise ValueError(f"Could not find value: {name}")

    @staticmethod
    def get_value_resource(
        name: str, resources: ExternalResources, lines: List[str]
    ) -> Resource:
        value = TresParser.get_value(name, lines)

        matching = re.search("ExtResource\( (\d+) \)", value)
        if not matching:
            raise ValueError(
                f'Value for "{name}" was not an external resource: {value}'
            )

        index = int(matching.group(1))

        return resources.resources[index]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
