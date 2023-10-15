"""
Classes and methods for parsing Godot resource files.
"""
from dataclasses import dataclass
from typing import IO, List, Literal, Tuple, Union

import enum


@dataclass(frozen=True)
class ResourceHeader:
    """
    The header of a compiled Godot resource file.
    """

    header: str
    endian: Literal["big", "little"]
    string_map: List[str]
    int_resources: List[Tuple[str, int]]

    @staticmethod
    def from_stream(input_stream: IO[bytes]) -> "ResourceHeader":
        """
        Reads the ResourceHeader from the given input stream.

        Leaves the stream at the end of the header, so code calling it can continue parsing the
        rest of the file from there.
        """
        header = input_stream.read(4).decode("ascii")
        assert header == "RSRC"

        big_endian = input_stream.read(4) != b"\x00\x00\x00\x00"
        _use_real64 = input_stream.read(4) != b"\x00\x00\x00\x00"
        endian: Literal["big", "little"] = "big" if big_endian else "little"

        _engine_ver_major = int.from_bytes(input_stream.read(4), endian)
        _engine_ver_minor = int.from_bytes(input_stream.read(4), endian)
        _ver_format_bin = int.from_bytes(input_stream.read(4), endian)

        _resource_type = read_unicode_string(input_stream, endian)

        _importmd_ofs = int.from_bytes(input_stream.read(8), endian)
        _flags = int.from_bytes(input_stream.read(4), endian)

        # Skip over res_uid field
        input_stream.read(8)

        # Skip reserved fields
        for _ in range(0, 11):
            input_stream.read(4)

        string_table_size = int.from_bytes(input_stream.read(4), endian)
        string_map = [
            read_unicode_string(input_stream, endian)
            for _ in range(0, string_table_size)
        ]

        ext_resources_size = int.from_bytes(input_stream.read(4), endian)
        assert ext_resources_size == 0

        int_resources_size = int.from_bytes(input_stream.read(4), endian)
        int_resources = [
            (
                read_unicode_string(input_stream, endian),
                int.from_bytes(input_stream.read(8), endian),
            )
            for _ in range(0, int_resources_size)
        ]

        return ResourceHeader(
            header=header,
            endian=endian,
            string_map=string_map,
            int_resources=int_resources,
        )


PropertyValue = Union[List[bytes], List[int], str]


class VariantBin(enum.Enum):
    """
    Type ids for values in a Godot resource file.
    """

    VARIANT_NIL = 1
    VARIANT_BOOL = 2
    VARIANT_INT = 3
    VARIANT_REAL = 4
    VARIANT_FLOAT = 4
    VARIANT_STRING = 5
    VARIANT_VECTOR2 = 10
    VARIANT_RECT2 = 11
    VARIANT_VECTOR3 = 12
    VARIANT_PLANE = 13
    VARIANT_QUAT = 14
    VARIANT_AABB = 15
    VARIANT_MATRIX3 = 16
    VARIANT_TRANSFORM = 17
    VARIANT_MATRIX32 = 18
    VARIANT_COLOR = 20
    VARIANT_IMAGE = 21
    VARIANT_NODE_PATH = 22
    VARIANT_RID = 23
    VARIANT_OBJECT = 24
    VARIANT_INPUT_EVENT = 25
    VARIANT_DICTIONARY = 26
    VARIANT_ARRAY = 30
    VARIANT_RAW_ARRAY = 31
    VARIANT_INT_ARRAY = 32
    VARIANT_INT32_ARRAY = 32
    VARIANT_REAL_ARRAY = 33
    VARIANT_FLOAT32_ARRAY = 33
    VARIANT_STRING_ARRAY = 34
    VARIANT_VECTOR3_ARRAY = 35
    VARIANT_COLOR_ARRAY = 36
    VARIANT_VECTOR2_ARRAY = 37
    VARIANT_INT64 = 40
    VARIANT_DOUBLE = 41
    VARIANT_CALLABLE = 42
    VARIANT_SIGNAL = 43
    VARIANT_STRING_NAME = 44
    VARIANT_VECTOR2I = 45
    VARIANT_RECT2I = 46
    VARIANT_VECTOR3I = 47
    VARIANT_PACKED_INT64_ARRAY = 48
    VARIANT_PACKED_FLOAT64_ARRAY = 49
    VARIANT_VECTOR4 = 50
    VARIANT_VECTOR4I = 51
    VARIANT_PROJECTION = 52


def read_unicode_string(
    input_stream: IO[bytes], endian: Literal["big", "little"]
) -> str:
    """
    Reads in a unicode string from the given input stream, using the given endianess.
    """
    length = int.from_bytes(input_stream.read(4), endian)
    buffer = input_stream.read(length)

    return buffer.decode("utf8")


def get_string(
    input_stream: IO[bytes], endian: Literal["big", "little"], string_map: List[str]
) -> str:
    """
    Reads in a unicode string from the given input stream, referencing the given string map in
    case the string is indexed into the map.
    """
    index = int.from_bytes(input_stream.read(4), endian)
    assert index < len(string_map), "Not yet supported"

    return string_map[index]


def read_variant(
    input_stream: IO[bytes], endian: Literal["big", "little"]
) -> PropertyValue:
    """
    Reads in a "variant" value from the given input stream.
    """
    t = int.from_bytes(input_stream.read(4), endian)

    v = VariantBin(t)
    if v == VariantBin.VARIANT_STRING:
        return read_unicode_string(input_stream, endian)
    elif v == VariantBin.VARIANT_RAW_ARRAY:
        length = int.from_bytes(input_stream.read(4), endian)
        values_bytes: List[bytes] = [input_stream.read(1) for _ in range(0, length)]

        extra = 4 - (length % 4)
        if extra < 4:
            for _ in range(0, extra):
                input_stream.read(1)

        return values_bytes
    elif v == VariantBin.VARIANT_INT32_ARRAY:
        length = int.from_bytes(input_stream.read(4), endian)
        values_ints: List[int] = [
            int.from_bytes(input_stream.read(4), endian) for _ in range(0, length)
        ]

        return values_ints
    else:
        raise NotImplementedError(f"t={t}")

    raise NotImplementedError()
