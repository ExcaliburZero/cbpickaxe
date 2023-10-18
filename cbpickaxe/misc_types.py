"""
Miscellaneous data types.

Many of these are simple dataclass re-implementations of Godot datatypes, which makes them easy to
write out to JSON.
"""
from dataclasses import dataclass

import godot_parser as gp


@dataclass(frozen=True)
class Color:
    """
    A RGBA color.

    Exists primarily to be a JSON serializable alternative to godot_parser's Color class.
    """

    red: float
    green: float
    blue: float
    alpha: float

    @staticmethod
    def from_gp(original: gp.Color) -> "Color":
        """
        Converts the given godot_parser Color into a cbpickaxe Color.
        """
        return Color(
            red=original.r,
            green=original.g,
            blue=original.b,
            alpha=original.a,
        )


@dataclass(frozen=True)
class Vector2:
    """
    A 2D vector.
    """

    x: float
    y: float


@dataclass(frozen=True)
class Rect2:
    """
    A 2D rectangle.
    """

    position: Vector2
    size: Vector2
