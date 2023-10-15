"""
Classes related to translating in-game string ids to localized strings.
"""
from dataclasses import dataclass
from typing import cast, IO, List, Optional, Tuple

import smaz

from .resource import (
    ResourceHeader,
    PropertyValue,
    read_unicode_string,
    get_string,
    read_variant,
)


class TranslationTable:
    """
    Key value mapping of in-game string ids to localized strings.

    This mapping does not store the strings, because the Godot ".translation" files that we load
    the data from do not store they keys. Thos files only store hashes of the keys, hash buckets
    for looking up the localized strings, and the localized strings.
    """

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
        hashes: List[int],
        buckets: List[int],
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
        header = ResourceHeader.from_stream(input_stream)

        for i, (_, offset) in enumerate(header.int_resources):
            main = i == (len(header.int_resources) - 1)
            assert main

            input_stream.seek(offset)
            _rtype = read_unicode_string(input_stream, header.endian)

            pc = int.from_bytes(input_stream.read(4), header.endian)

            properties: List[Tuple[str, PropertyValue]] = []
            for _ in range(0, pc):
                name = get_string(input_stream, header.endian, header.string_map)
                variant = read_variant(input_stream, header.endian, header.string_map)

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

            assert isinstance(strings, list)
            assert isinstance(strings[0], bytes)
            strings = cast(List[bytes], strings)

            assert isinstance(hashes, list)
            for h in hashes:
                assert isinstance(h, int)
            hashes = cast(List[int], hashes)

            assert isinstance(buckets, list)
            for b in buckets:
                assert isinstance(b, int)
            buckets = cast(List[int], buckets)

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
        hashes: List[int],
        buckets: List[int],
        strings: List[bytes],
        string: str,
    ) -> str:
        h = TranslationTable.__hash(0, string)

        h_hash = hashes[h % len(hashes)]

        assert isinstance(h_hash, int)
        if h_hash == 0xFFFFFFFF:
            raise KeyError(string)

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
