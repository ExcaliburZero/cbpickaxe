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

    red: float  #: Red component in the range of [0.0, 1.0].
    green: float  #: Green component in the range of [0.0, 1.0].
    blue: float  #: Blue component in the range of [0.0, 1.0].
    alpha: float  #: Alpha/opacity of the color in the range of [0.0, 1.0], where 1.0 indicates fully opaque and 0.0 indicates fully transparent.

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

    x: float  #: x component of the vector.
    y: float  #: y component of the vector.


@dataclass(frozen=True)
class Rect2:
    """
    A 2D rectangle.
    """

    position: Vector2  #: Position of the top left corner of the rectangle.
    size: Vector2  #: Width (x) and height (y) of the rectangle.
