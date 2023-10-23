"""
Classes related to items.
"""
from dataclasses import dataclass
from typing import IO, Optional

import godot_parser as gp


@dataclass
class Item:
    """
    An item that the player can obtain.
    """

    name: str  #: String ID of the name of the item.
    description: str  #: String ID of the description of the item.
    category: str
    icon: Optional[str]  #: res:// path to the item's icon.

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "Item":
        """
        Parses an Item from the given Godot ".tres" input stream.
        """
        scene = gp.parse(input_stream.read())

        name = None
        description = None
        category = None
        icon = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                name = section["name"]
                description = section["description"]
                category = section["category"]
                icon = Item.__parse_icon(scene, section)

        assert isinstance(name, str)
        assert isinstance(description, str)
        assert isinstance(category, str)
        assert isinstance(icon, str) or icon is None

        return Item(
            name=name,
            description=description,
            category=category,
            icon=icon,
        )

    @staticmethod
    def __parse_icon(scene: gp.GDFile, section: gp.GDResourceSection) -> Optional[str]:
        try:
            icon_resource = section["icon"]
        except KeyError:
            return None

        assert isinstance(icon_resource, gp.ExtResource)
        icon_ext_resource = scene.find_ext_resource(id=icon_resource.id)
        assert icon_ext_resource is not None
        icon = icon_ext_resource.path

        return icon
