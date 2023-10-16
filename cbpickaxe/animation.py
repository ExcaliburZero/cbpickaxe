"""
Classes related to sprite animations.
"""
from dataclasses import dataclass
from typing import Any, cast, Dict, IO, List, Optional, Tuple

from .resource import (
    ResourceHeader,
    read_unicode_string,
    read_variant,
    get_string,
    PropertyValue,
    InternalResourceIndex,
    Rect2,
)


@dataclass(frozen=True)
class Box:
    """
    A rectangular region of an image.
    """

    x: int
    y: int
    width: int
    height: int

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Box":
        """
        Converts the given dict into a Box.
        """
        x = d["x"]
        y = d["y"]
        w = d["w"]
        h = d["h"]

        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(w, int)
        assert isinstance(h, int)

        return Box(x, y, w, h)


@dataclass(frozen=True)
class Frame:
    """
    A frame that can be used in animations.
    """

    box: Box

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Frame":
        """
        Converts the given dict into a Frame.
        """
        box = Box.from_dict(d["frame"])

        return Frame(box)


@dataclass
class FrameTag:
    """
    A tag descripting the frames of an animation.
    """

    name: str
    start_frame: int
    end_frame: int

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "FrameTag":
        """
        Converts the given dict into a FrameTag.
        """
        name = d["name"]
        start_frame = d["from"]
        end_frame = d["to"]

        assert isinstance(name, str)
        assert isinstance(start_frame, int)
        assert isinstance(end_frame, int)

        return FrameTag(name, start_frame, end_frame)


@dataclass
class FrameChain:
    frames: List[Frame]

    def merge(self, other: "FrameChain") -> bool:
        overlap = self.get_overlap(other)
        if overlap is None:
            return False

        new_frames_order = self.frames

        if overlap[0][0] == 0 and overlap[0][1] != 0:
            new_frames_order = other.frames[0 : overlap[0][1]] + new_frames_order

        if (
            overlap[1][0] == len(self.frames) - 1
            and overlap[1][1] != len(other.frames) - 1
        ):
            new_frames_order = new_frames_order + other.frames[overlap[1][1] :]

        return True

    def get_overlap(
        self, other: "FrameChain"
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        # Find one overlapping frame to start the search with
        one_overlap = None
        for i, frame_a in enumerate(self.frames):
            for j, frame_b in enumerate(other.frames):
                if frame_a == frame_b:
                    one_overlap = (i, j)

        if one_overlap is None:
            return None

        overlap_start = one_overlap
        overlap_end = one_overlap

        # Widen out the overlap window backwards
        while overlap_start[0] >= 1 and overlap_start[1] >= 1:
            frame_a = self.frames[overlap_start[0] - 1]
            frame_b = other.frames[overlap_start[1] - 1]

            if frame_a == frame_b:
                overlap_start = (overlap_start[0] - 1, overlap_start[1] - 1)
            else:
                break

        # Widen out the overlap window forwards
        while (
            overlap_end[0] < len(self.frames) - 1
            and overlap_end[1] < len(other.frames) - 1
        ):
            frame_a = self.frames[overlap_end[0] + 1]
            frame_b = other.frames[overlap_end[1] + 1]

            if frame_a == frame_b:
                overlap_end = (overlap_end[0] + 1, overlap_end[1] + 1)
            else:
                break

        return overlap_start, overlap_end


@dataclass
class Animation:
    """
    An animated sprite consisting of a set of frames with several tags indicating types of
    animations (ex. idle, attack, hurt),
    """

    frames: List[Frame]
    frame_tags: List[FrameTag]
    image: str

    def get_frame(self, animation_name: str, frame_offset: int) -> Frame:
        """
        Returns the frame at the given offset within the animation with the given name.
        """
        return self.frames[
            self.get_frame_tag(animation_name).start_frame + frame_offset
        ]

    def get_frame_tag(self, name: str) -> FrameTag:
        """
        Returns the FrameTag with the given name.
        """
        for frame_tag in self.frame_tags:
            if frame_tag.name == name:
                return frame_tag

        raise KeyError(name)

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Animation":
        """
        Converts the given dict into an Animation.
        """
        frames = [
            Frame.from_dict(data)
            for name, data in sorted(
                d["frames"].items(), key=lambda e: Animation.__get_frame_id(e[0])
            )
        ]
        frame_tags = [FrameTag.from_dict(entry) for entry in d["meta"]["frameTags"]]
        image = d["meta"]["image"]

        assert isinstance(image, str)

        return Animation(frames, frame_tags, image)

    @staticmethod
    def from_scn(input_stream: IO[bytes]) -> "Animation":
        """
        Reads in an Animation from the given Godot scn file input stream.
        """
        header = ResourceHeader.from_stream(input_stream)

        assert len(header.ext_resources) == 1, header.ext_resources
        image = header.ext_resources[0][1].replace("\x00", "")

        sections = []
        main_section_ = None
        for i, (_, offset) in enumerate(header.int_resources):
            main = i == (len(header.int_resources) - 1)

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

            if main:
                main_section_ = properties_by_name

            sections.append(properties_by_name)

        assert main_section_ is not None
        assert isinstance(main_section_, dict)
        for key, value in main_section_.items():
            assert isinstance(key, str)
            assert isinstance(value, dict)
            for key_2 in value.keys():
                assert isinstance(key_2, str)
        main_section: Dict[str, Dict[str, PropertyValue]] = cast(
            Dict[str, Dict[str, PropertyValue]], main_section_
        )

        names = main_section["_bundled"]["names\x00"]
        variants = main_section["_bundled"]["variants\u0000"]

        assert isinstance(names, list)
        for n in names:
            assert isinstance(n, str)
        names = cast(List[str], names)

        assert isinstance(variants, list)
        variants = cast(List[Any], variants)

        animations_dict = {}
        for n, v in zip(names, variants):
            if n.startswith("anims/"):
                animations_dict[n.replace("\x00", "")] = v

        animations = {}
        for animation_name, v in animations_dict.items():
            if isinstance(v, InternalResourceIndex):
                data_ = sections[v.index - 1]["tracks/0/keys"]

                assert isinstance(data_, dict)
                for key in data_:
                    assert isinstance(key, str)
                data = cast(Dict[str, Any], data_)

                animation_frames = []
                for rect_2 in data["values\x00"]:
                    assert isinstance(rect_2, Rect2)
                    frame = Frame(
                        Box(
                            x=round(rect_2.position.x),
                            y=round(rect_2.position.y),
                            width=round(rect_2.size.x),
                            height=round(rect_2.size.y),
                        )
                    )

                    animation_frames.append(frame)

                animations[animation_name] = animation_frames

        frames, frame_tags = Animation.__reconstruct_frames_info(animations)

        return Animation(frames, frame_tags, image)

    @staticmethod
    def __reconstruct_frames_info(
        animations: Dict[str, List[Frame]]
    ) -> Tuple[List[Frame], List[FrameTag]]:
        frame_chains = [FrameChain(frames) for _, frames in animations.items()]
        any_changes = True
        while any_changes:
            any_changes = False

            i = 0
            while i < len(frame_chains):
                j = i + 1
                while j < len(frame_chains):
                    a = frame_chains[i]
                    b = frame_chains[j]

                    if a.merge(b):
                        del frame_chains[j]
                        j -= 1

                        any_changes = True

                    j += 1

                i += 1

        frames: List[Frame] = [
            *[frame for chain in frame_chains for frame in chain.frames]
        ]
        assert len(frames) == len(set(frames)), f"{len(frames)} != {len(set(frames))}"

        # Create frame tags
        frame_tags = []
        for animation_name, animation_frames in animations.items():
            start_frame = frames.index(animation_frames[0])
            end_frame = frames.index(animation_frames[-1])

            # Double check that the frame ordering is valid
            for i, j in zip(
                range(0, len(animation_frames) - 1), range(1, len(animation_frames))
            ):
                assert i == j - 1
                c = frames.index(animation_frames[i])
                d = frames.index(animation_frames[j])
                assert c == d - 1

            frame_tags.append(FrameTag(animation_name, start_frame, end_frame))

        return frames, frame_tags

    @staticmethod
    def __get_frame_id(frame_name: str) -> int:
        return int(frame_name.split(" ")[-1].split(".")[0])
