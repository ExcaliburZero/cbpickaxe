"""
Classes related to sprite animations.
"""
from dataclasses import dataclass
from typing import Any, Dict, IO, List

from .resource import ResourceHeader


@dataclass
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


@dataclass
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
        print(header)

        assert len(header.ext_resources) == 1, header.ext_resources
        image = header.ext_resources[0][1].replace("\x00", "")
        print(image)

        raise NotImplementedError()

    @staticmethod
    def __get_frame_id(frame_name: str) -> int:
        return int(frame_name.split(" ")[-1].split(".")[0])
