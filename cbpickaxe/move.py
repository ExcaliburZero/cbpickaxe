"""
Classes related to moves / stickers.
"""
from dataclasses import dataclass
from typing import cast, IO, List

import godot_parser as gp


@dataclass
class Move:
    """
    A move / sticker that monsters can use in battle.
    """

    name: str
    category_name: str
    description: str
    cost: int
    is_passive_only: bool
    power: int
    accuracy: int
    unavoidable: bool
    tags: List[str]
    elemental_types: List[str]

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
