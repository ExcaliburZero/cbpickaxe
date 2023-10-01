from dataclasses import dataclass
from typing import cast, Dict, IO, List, Literal, Tuple, Union

import enum

import smaz


PropertyValue = Union[List[bytes], List[int]]


class VariantBin(enum.Enum):
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
class Bucket:
    size: int
    func: int
    key: int
    str_offset: int
    comp_size: int
    uncomp_size: int

    @staticmethod
    def from_ints(ints: List[int]) -> "Bucket":
        return Bucket(*ints)


@dataclass
class TranslationTable:
    messages: Dict[str, str]

    @staticmethod
    def from_translation(input_stream: IO[bytes]) -> "TranslationTable":
        header = input_stream.read(4).decode("ascii")
        assert header == "RSRC"

        big_endian = input_stream.read(4) != b"\x00\x00\x00\x00"
        use_real64 = input_stream.read(4) != b"\x00\x00\x00\x00"
        endian: Literal["big", "little"] = "big" if big_endian else "little"
        print(f"big_endian: {big_endian}")
        print(f"use_real64: {use_real64}")

        engine_ver_major = int.from_bytes(input_stream.read(4), endian)
        engine_ver_minor = int.from_bytes(input_stream.read(4), endian)
        ver_format_bin = int.from_bytes(input_stream.read(4), endian)
        print(f"engine_ver_major: {engine_ver_major}")
        print(f"engine_ver_minor: {engine_ver_minor}")
        print(f"ver_format_bin: {ver_format_bin}")

        resource_type = TranslationTable.__read_unicode_string(input_stream, endian)
        print(f"resource_type: {resource_type}")

        importmd_ofs = int.from_bytes(input_stream.read(8), endian)
        flags = int.from_bytes(input_stream.read(4), endian)
        print(f"importmd_ofs: {importmd_ofs}")
        print(f"flags: {flags}")

        # Skip over res_uid field
        input_stream.read(8)

        # Skip reserved fields
        for _ in range(0, 11):
            input_stream.read(4)

        string_table_size = int.from_bytes(input_stream.read(4), endian)
        print(f"string_table_size: {string_table_size}")

        string_map = [
            TranslationTable.__read_unicode_string(input_stream, endian)
            for _ in range(0, string_table_size)
        ]

        print(f"string_map: {string_map}")

        ext_resources_size = int.from_bytes(input_stream.read(4), endian)
        assert ext_resources_size == 0
        print(f"ext_resources_size: {ext_resources_size}")

        int_resources_size = int.from_bytes(input_stream.read(4), endian)
        print(f"int_resources_size: {int_resources_size}")

        int_resources = [
            (
                TranslationTable.__read_unicode_string(input_stream, endian),
                int.from_bytes(input_stream.read(8), endian),
            )
            for _ in range(0, int_resources_size)
        ]
        print(f"int_resources: {int_resources}")

        for i, (path, offset) in enumerate(int_resources):
            print(f"i={i}, path={path}, offset={offset}")

            main = i == (len(int_resources) - 1)
            print(f"  main: {main}")
            assert main

            # TODO: local path???
            # https://github.com/bruvzg/gdsdecomp/blob/4314628d790d2d37c78ad7855e3a0e21dfaf0677/compat/resource_loader_compat.cpp#L914

            input_stream.seek(offset)
            rtype = TranslationTable.__read_unicode_string(input_stream, endian)
            print(f"  rtype: {rtype}")

            pc = int.from_bytes(input_stream.read(4), endian)
            print(f"  pc: {pc}")

            properties: List[Tuple[str, PropertyValue]] = []
            for j in range(0, pc):
                print(f"    location: {input_stream.tell()}")
                name = TranslationTable.__get_string(input_stream, endian, string_map)
                print(f"    name: {name}")

                variant = TranslationTable.__read_variant(input_stream, endian)
                print(f"    variant: {variant}")

                properties.append((name, variant))

            print(f"  properties: {[(n, type(v)) for n, v in properties]}")

            """
            hashes = properties[0][1]
            print(properties[0][0])

            buckets = properties[1][1]

            messages: Dict[str, str] = {}
            for hash in hashes:
                assert isinstance(hash, int)
                buckets = cast(List[int], buckets)

                s = ""
                if hash == 0xFFFFFFFF:
                    continue

                BUCKET_SIZE = 6
                print(buckets[0])
                bucket = Bucket.from_ints(buckets[hash : hash + BUCKET_SIZE])
                print(bucket)

                h = TranslationTable.__hash(bucket.func, )
            """

            strings = cast(List[bytes], properties[2][1])

            translation_strings: List[str] = []
            for string_bytes in TranslationTable.__split_list(strings, b"\x00"):
                try:
                    translation_strings.append(string_bytes.decode("utf8"))
                    print(translation_strings[-1])
                    print(smaz.compress(string_bytes.decode("utf8")))
                    print(smaz.decompress(smaz.compress(string_bytes.decode("utf8"))))
                except UnicodeDecodeError:
                    print(string_bytes)
                    translation_strings.append(smaz.decompress(string_bytes))
                    print(translation_strings[-1])

            messages = {f"{i}": msg for i, msg in enumerate(translation_strings)}

            return TranslationTable(messages)

        raise NotImplementedError()

    @staticmethod
    def __hash(d: int, value: str) -> int:
        str_bytes = value.encode("utf8")

        if d == 0:
            d = 0x1000193

        for b in str_bytes:
            d = (d * 0x1000193) ** b

        return d

    @staticmethod
    def __split_list(l: List[bytes], value: bytes) -> List[bytes]:
        groups = []

        buffer: List[bytes] = []
        for v in l:
            if v == value:
                groups.append(buffer)
                buffer = []
            else:
                buffer.append(v)

        if len(buffer) > 0:
            groups.append(buffer)

        return [b"".join(g) for g in groups]

    @staticmethod
    def __get_string(
        input_stream: IO[bytes], endian: Literal["big", "little"], string_map: List[str]
    ) -> str:
        index = int.from_bytes(input_stream.read(4), endian)
        print(f"index={index}")
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

        print(f"    t: {t}")

        v = VariantBin(t)

        if v == VariantBin.VARIANT_RAW_ARRAY:
            length = int.from_bytes(input_stream.read(4), endian)
            print(f"    length: {length}")
            values_bytes: List[bytes] = [input_stream.read(1) for _ in range(0, length)]

            extra = 4 - (length % 4)
            print(f"    extra: {extra}")
            if extra < 4:
                for _ in range(0, extra):
                    input_stream.read(1)

            return values_bytes
        elif v == VariantBin.VARIANT_INT32_ARRAY:
            length = int.from_bytes(input_stream.read(4), endian)
            print(f"    length: {length}")
            values_ints: List[int] = [
                int.from_bytes(input_stream.read(4), endian) for _ in range(0, length)
            ]

            return values_ints
        else:
            raise NotImplementedError(f"t={t}")

        raise NotImplementedError()
