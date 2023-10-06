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
    tags: List[str]

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "Move":
        """
        Parses a Move from the given Godot ".tres" input stream.
        """
        scene = gp.parse(input_stream.read())

        name = None
        category_name = None
        description = None
        tags = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                name = section["name"]
                category_name = section["category_name"]
                description = section["description"]
                tags = section["tags"]

        assert isinstance(name, str)
        assert isinstance(category_name, str)
        assert isinstance(description, str)
        assert isinstance(tags, list)

        for tag in tags:
            assert isinstance(tag, str)
        tags = cast(List[str], tags)

        return Move(
            name=name, category_name=category_name, description=description, tags=tags
        )
