"""
Classes related to items.
"""
from dataclasses import dataclass
from typing import IO

import godot_parser as gp


@dataclass
class Item:
    """
    An item that the player can obtain.
    """

    name: str

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "Item":
        """
        Parses an Item from the given Godot ".tres" input stream.
        """
        scene = gp.parse(input_stream.read())

        name = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                name = section["name"]

        assert isinstance(name, str)

        return Item(
            name=name,
        )
