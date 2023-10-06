"""
Classes related to translating in-game string ids to localized strings.
"""
from dataclasses import dataclass
from typing import cast, IO, List, Literal, Optional, Tuple, Union

import enum

import smaz


class TranslationTable:
    """
    Key value mapping of in-game string ids to localized strings.

    This mapping does not store the strings, because the Godot ".translation" files that we load
    the data from do not store they keys. Thos files only store hashes of the keys, hash buckets
    for looking up the localized strings, and the localized strings.
    """

    PropertyValue = Union[List[bytes], List[int], str]

    class _VariantBin(enum.Enum):
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

    @dataclass
    class _BucketElement:
        key: int
        str_offset: int
        comp_size: int
        uncomp_size: int

        @staticmethod
        def from_ints(ints: List[int]) -> "TranslationTable._BucketElement":
            """
            Converts ints into a BucketElement.
            """
            # pylint: disable-next=protected-access
            return TranslationTable._BucketElement(*ints)

    @dataclass
    class _Bucket:
        size: int
        func: int
        elements: List["TranslationTable._BucketElement"]

        @staticmethod
        def from_ints(ints: List[int]) -> "TranslationTable._Bucket":
            """
            Converts ints into a Bucket.
            """
            # pylint: disable-next=protected-access
            return TranslationTable._Bucket(
                ints[0],
                ints[1],
                [
                    # pylint: disable-next=protected-access
                    TranslationTable._BucketElement.from_ints(
                        ints[2 + i * 4 : 2 + (i + 1) * 4]
                    )
                    for i in range(0, ints[0])
                ],
            )

    def __init__(
        self,
        hashes: PropertyValue,
        buckets: PropertyValue,
        strings: List[bytes],
    ) -> None:
        self.__hashes = hashes
        self.__buckets = buckets
        self.__strings = strings

    @staticmethod
    def from_translation(input_stream: IO[bytes]) -> Tuple["TranslationTable", str]:
        """
        Creates a TranslationTable from the given binary input stream of a Godot ".translation"
        file.

        Returns both the table and the locale. The locale defaults to English (en) if no locale is
        listed in the given ".translation" file.
        """
        header = input_stream.read(4).decode("ascii")
        assert header == "RSRC"

        big_endian = input_stream.read(4) != b"\x00\x00\x00\x00"
        _use_real64 = input_stream.read(4) != b"\x00\x00\x00\x00"
        endian: Literal["big", "little"] = "big" if big_endian else "little"

        _engine_ver_major = int.from_bytes(input_stream.read(4), endian)
        _engine_ver_minor = int.from_bytes(input_stream.read(4), endian)
        _ver_format_bin = int.from_bytes(input_stream.read(4), endian)

        _resource_type = TranslationTable.__read_unicode_string(input_stream, endian)

        _importmd_ofs = int.from_bytes(input_stream.read(8), endian)
        _flags = int.from_bytes(input_stream.read(4), endian)

        # Skip over res_uid field
        input_stream.read(8)

        # Skip reserved fields
        for _ in range(0, 11):
            input_stream.read(4)

        string_table_size = int.from_bytes(input_stream.read(4), endian)
        string_map = [
            TranslationTable.__read_unicode_string(input_stream, endian)
            for _ in range(0, string_table_size)
        ]

        ext_resources_size = int.from_bytes(input_stream.read(4), endian)
        assert ext_resources_size == 0

        int_resources_size = int.from_bytes(input_stream.read(4), endian)
        int_resources = [
            (
                TranslationTable.__read_unicode_string(input_stream, endian),
                int.from_bytes(input_stream.read(8), endian),
            )
            for _ in range(0, int_resources_size)
        ]

        for i, (_, offset) in enumerate(int_resources):
            main = i == (len(int_resources) - 1)
            assert main

            input_stream.seek(offset)
            _rtype = TranslationTable.__read_unicode_string(input_stream, endian)

            pc = int.from_bytes(input_stream.read(4), endian)

            properties: List[Tuple[str, TranslationTable.PropertyValue]] = []
            for _ in range(0, pc):
                name = TranslationTable.__get_string(input_stream, endian, string_map)
                variant = TranslationTable.__read_variant(input_stream, endian)

                properties.append((name, variant))

            properties_by_name = {
                prop[0].rstrip("\x00"): prop[1] for prop in properties
            }

            hashes = properties_by_name["hash_table"]
            buckets = properties_by_name["bucket_table"]
            strings = properties_by_name["strings"]

            locale = properties_by_name.get("locale", "en")
            assert isinstance(locale, str)
            locale = locale.replace("\x00", "")

            assert isinstance(strings[0], bytes)
            strings = cast(List[bytes], strings)

            return TranslationTable(hashes, buckets, strings), locale

        raise NotImplementedError()

    def __getitem__(self, key: str) -> str:
        return TranslationTable.__get(
            self.__hashes, self.__buckets, self.__strings, key
        )

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Looks up the translation of the given string id.

        If the given string id is not found and a default value was provided, then the default
        value will be returned.
        """
        try:
            return self[key]
        except KeyError as e:
            if default is not None:
                return default
            else:
                raise e

    @staticmethod
    def __get(
        hashes: PropertyValue,
        buckets: PropertyValue,
        strings: List[bytes],
        string: str,
    ) -> str:
        h = TranslationTable.__hash(0, string)

        h_hash = hashes[h % len(hashes)]

        assert isinstance(h_hash, int)
        if h_hash == 0xFFFFFFFF:
            raise KeyError(string)

        buckets = cast(List[int], buckets)
        bucket_size = buckets[h_hash]
        bucket = TranslationTable._Bucket.from_ints(
            buckets[h_hash : h_hash + 2 + 4 * bucket_size]
        )

        h = TranslationTable.__hash(bucket.func, string)

        for e in bucket.elements:
            if e.key == h:
                value_bytes = b"".join(
                    strings[e.str_offset : e.str_offset + e.comp_size]
                )

                if e.comp_size == e.uncomp_size:
                    value = value_bytes.decode("utf8")
                else:
                    value = smaz.decompress(value_bytes)

                assert isinstance(value, str)

                return value.rstrip("\x00")

        raise KeyError(string)

    @staticmethod
    def __hash(d: int, value: str) -> int:
        # https://github.com/MaxStgs/godot/blob/31d0f8ad8d5cf50a310ee7e8ada4dcdb4510690b/core/compressed_translation.h#L66-L77
        str_bytes = value.encode("utf8")

        if d == 0:
            d = 0x1000193

        for b in str_bytes:
            d = ((d * 0x1000193) % 0x100000000) ^ b

        return d

    @staticmethod
    def __get_string(
        input_stream: IO[bytes], endian: Literal["big", "little"], string_map: List[str]
    ) -> str:
        index = int.from_bytes(input_stream.read(4), endian)
        assert index < len(string_map), "Not yet supported"

        return string_map[index]

    @staticmethod
    def __read_unicode_string(
        input_stream: IO[bytes], endian: Literal["big", "little"]
    ) -> str:
        length = int.from_bytes(input_stream.read(4), endian)
        buffer = input_stream.read(length)

        return buffer.decode("utf8")

    @staticmethod
    def __read_variant(
        input_stream: IO[bytes], endian: Literal["big", "little"]
    ) -> PropertyValue:
        t = int.from_bytes(input_stream.read(4), endian)

        v = TranslationTable._VariantBin(t)
        if v == TranslationTable._VariantBin.VARIANT_STRING:
            return TranslationTable.__read_unicode_string(input_stream, endian)
        elif v == TranslationTable._VariantBin.VARIANT_RAW_ARRAY:
            length = int.from_bytes(input_stream.read(4), endian)
            values_bytes: List[bytes] = [input_stream.read(1) for _ in range(0, length)]

            extra = 4 - (length % 4)
            if extra < 4:
                for _ in range(0, extra):
                    input_stream.read(1)

            return values_bytes
        elif v == TranslationTable._VariantBin.VARIANT_INT32_ARRAY:
            length = int.from_bytes(input_stream.read(4), endian)
            values_ints: List[int] = [
                int.from_bytes(input_stream.read(4), endian) for _ in range(0, length)
            ]

            return values_ints
        else:
            raise NotImplementedError(f"t={t}")

        raise NotImplementedError()
