"""
Classes related to sprite animations.
"""
from dataclasses import dataclass
from typing import Any, cast, Dict, IO, Iterator, List, Tuple

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

    x: int  #: Left-most position of the Box.
    y: int  #: Upper-most position of the Box.
    width: int  #: Width of the Box.
    height: int  #: Height of the Box.

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

    box: Box  #: Box that defines the area on the sprite sheet that makes up the frame.

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

    name: str  #: Name of the FrameTag, typically the name of the animation (ex. "idle").
    start_frame: int  #: Id of the first frame that makes up the animation.
    end_frame: int  #: Id of the last frame that makes up the animation.

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
class Animation:
    """
    An animated sprite consisting of a set of frames with several tags indicating types of
    animations (ex. idle, attack, hurt),
    """

    frames: List[
        Frame
    ]  #: Frames that make up the animations. Can be indexed into using the frame ids stored in FrameTags.
    frame_tags: List[
        FrameTag
    ]  #: Information on specific animations (ex. "idle", "atttack", etc.)
    image: str  #: Relative filepath to the sprite sheet image for the animation.

    def __iter__(self) -> Iterator[str]:
        return (frame_tag.name for frame_tag in self.frame_tags)

    def __getitem__(self, key: str) -> Tuple[FrameTag, List[Frame]]:
        for frame_tag in self.frame_tags:
            if frame_tag.name == key:
                frames = self.frames[frame_tag.start_frame : frame_tag.end_frame]

                return frame_tag, frames

        raise KeyError(key)

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
        image = header.ext_resources[0][1].replace("\x00", "").split("/")[-1]

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
        animation_names = []
        for n in names:
            if n.startswith("anims/"):
                animation_names.append(n.replace("\x00", ""))

        # Note: This assumes that the internal resources are exactly 1 informational resource, all
        # the animations in the same order as they are in the names section, and the main resource.
        #
        # I don't have a good reason for why this works, but it seems that it does.
        #
        # The names and variants do not mach up in order, so this was the only was I was able to
        # get the correct animation frames for each animation.
        for i, animation_name in enumerate(animation_names):
            animations_dict[animation_name] = InternalResourceIndex(index=1 + i)

        animations = {}
        for animation_name, v in animations_dict.items():
            if isinstance(v, InternalResourceIndex):
                data_ = sections[v.index]["tracks/0/keys"]

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

                animations[animation_name.replace("anims/", "")] = animation_frames

        frames, frame_tags = Animation.__reconstruct_frames_info(animations)

        return Animation(frames, frame_tags, image)

    @staticmethod
    def __reconstruct_frames_info(
        animations: Dict[str, List[Frame]]
    ) -> Tuple[List[Frame], List[FrameTag]]:
        # Note: I originally used a more complex scheme where I tried to pack together re-used
        # frames, but that ran into issues that I was unable to fix.

        frame_tags = []
        frames: List[Frame] = []
        for animation_name, animation_frames in animations.items():
            start_frame = len(frames)
            end_frame = len(frames) + len(animation_frames)

            frames += animation_frames

            frame_tags.append(FrameTag(animation_name, start_frame, end_frame))

        return frames, frame_tags

    @staticmethod
    def __get_frame_id(frame_name: str) -> int:
        return int(frame_name.split(" ")[-1].split(".")[0])
