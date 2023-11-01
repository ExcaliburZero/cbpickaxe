from dataclasses import dataclass
from typing import cast, IO, List

import godot_parser as gp

from .misc_types import Color


@dataclass
class ElementalType:
    palette: List[Color]

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "ElementalType":
        scene = gp.parse(input_stream.read())

        palette = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                palette = section["palette"]

        assert isinstance(palette, list)

        for color in palette:
            assert isinstance(color, gp.Color)
        palette = cast(List[gp.Color], palette)

        return ElementalType(palette=[Color.from_gp(color) for color in palette])
