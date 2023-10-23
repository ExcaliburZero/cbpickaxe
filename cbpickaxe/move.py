"""
Classes related to moves / stickers.
"""
from dataclasses import dataclass
from typing import cast, IO, List, Optional

import enum

import godot_parser as gp


class TargetType(enum.Enum):
    """
    The targets that a move can/will hit (single, team, etc.).
    """

    TARGET_NONE = 0
    TARGET_ONE = 1
    TARGET_TEAM = 2
    TARGET_ALL = 3
    TARGET_ONE_ALLY = 4
    TARGET_ONE_ALLY_NOT_SELF = 5
    TARGET_ONE_ENEMY = 6
    TARGET_ALL_NOT_SELF = 7

    def to_name(self) -> Optional[str]:
        """
        Converts the TargetType into the string that would be shown on the wiki.
        """
        if self == TargetType.TARGET_NONE:
            return None
        elif self == TargetType.TARGET_ONE:
            return "Single"
        elif self == TargetType.TARGET_TEAM:
            return "Team"
        elif self == TargetType.TARGET_ONE_ALLY:
            return "Single Ally"

        return str(self)


@dataclass
class Move:
    """
    A move / sticker that monsters can use in battle.
    """

    name: str  #: String ID of the name of the move.
    category_name: str
    description: str  #: String ID of the description of the move.
    cost: int  #: AP cost of the move.
    is_passive_only: bool  #: If True, then the move only has a passive effect.
    power: int  #: Power of the move.
    accuracy: int  #: Accuracy of the move.
    unavoidable: bool  #: If True, then the move is unavoidable, and thus guarenteed to hit.
    target_type: TargetType
    min_hits: int
    max_hits: int
    can_be_copied: bool
    priority: int
    tags: List[str]  #: Tags that determine which monsters can use the move.
    elemental_types: List[str]  #: Type(s) of the move.

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "Move":
        """
        Parses a Move from the given Godot ".tres" input stream.
        """
        scene = gp.parse(input_stream.read())

        name = None
        category_name = None
        description = None
        cost = None
        is_passive_only = None
        power = None
        accuracy = None
        unavoidable = None
        target_type = None
        min_hits = None
        max_hits = None
        can_be_copied = None
        priority = None
        tags = None
        elemental_types = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                name = section["name"]
                category_name = section["category_name"]
                description = section["description"]
                cost = section["cost"]
                is_passive_only = section["is_passive_only"]
                power = section["power"]
                accuracy = section["accuracy"]
                unavoidable = section["unavoidable"]
                target_type = section["target_type"]
                min_hits = section.get("min_hits", 0)
                max_hits = section.get("max_hits", 0)
                can_be_copied = section["can_be_copied"]
                priority = section["priority"]
                tags = section["tags"]
                elemental_types = Move.__parse_elemental_types(scene, section)

        assert isinstance(name, str)
        assert isinstance(category_name, str)
        assert isinstance(description, str)
        assert isinstance(cost, int)
        assert isinstance(is_passive_only, bool)
        assert isinstance(power, int)
        assert isinstance(accuracy, int)
        assert isinstance(unavoidable, bool)
        assert isinstance(target_type, int)
        assert isinstance(min_hits, int)
        assert isinstance(max_hits, int)
        assert isinstance(can_be_copied, bool)
        assert isinstance(priority, int)
        assert isinstance(tags, list)
        assert elemental_types is not None

        for tag in tags:
            assert isinstance(tag, str)
        tags = cast(List[str], tags)

        return Move(
            name=name,
            category_name=category_name,
            description=description,
            cost=cost,
            is_passive_only=is_passive_only,
            power=power,
            accuracy=accuracy,
            unavoidable=unavoidable,
            target_type=TargetType(target_type),
            min_hits=min_hits,
            max_hits=max_hits,
            can_be_copied=can_be_copied,
            priority=priority,
            tags=tags,
            elemental_types=elemental_types,
        )

    @staticmethod
    def __parse_elemental_types(
        scene: gp.GDFile, section: gp.GDResourceSection
    ) -> List[str]:
        elemental_types_raw = section["elemental_types"]
        elemental_types = []
        for raw_type in elemental_types_raw:
            ext_resource = scene.find_ext_resource(id=raw_type.id)
            assert ext_resource is not None

            elemental_type = ext_resource.path.split("/")[-1].split(".tres")[0]
            elemental_types.append(elemental_type)

        return elemental_types
