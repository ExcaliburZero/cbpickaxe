# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from typing import DefaultDict, List, Optional

import argparse
import collections
import pathlib
import sys

import PIL.Image

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument(
        "--monster_form_paths",
        nargs="+",
        default=[
            "res://data/monster_forms/",
            "res://data/monster_forms_secret/",
            "res://data/monster_forms_unlisted/",
        ],
    )
    parser.add_argument("--output_directory", required=True)
    parser.add_argument("--crop", default=False, action="store_true")

    args = parser.parse_args(argv)

    hoylake = cbp.Hoylake()
    for i, root in enumerate(args.roots):
        hoylake.load_root(str(i), pathlib.Path(root))

    monsters = {}
    for monsters_path in args.monster_form_paths:
        if monsters_path.endswith(".tres"):
            monsters[monsters_path] = hoylake.load_monster_form(monsters_path)
        else:
            monsters.update(hoylake.load_monster_forms(monsters_path))

    output_directory = pathlib.Path(args.output_directory)
    output_directory.mkdir(exist_ok=True)

    seen_monster_names: DefaultDict[str, int] = collections.defaultdict(lambda: 0)
    for _, (_, monster_form) in sorted(monsters.items()):
        try:
            animation = hoylake.load_animation(monster_form.battle_sprite_path)
        except ValueError:
            print(
                f"Could not find animation JSON file at path: {monster_form.battle_sprite_path}"
            )
            return FAILURE

        image_filepath_relative = (
            "/".join(monster_form.battle_sprite_path.split("/")[:-1])
            + "/"
            + animation.image
        )

        image_filepath = hoylake.lookup_filepath(image_filepath_relative)
        source_image = PIL.Image.open(image_filepath)

        monster_name = hoylake.translate(monster_form.name)
        seen_monster_names[monster_name] += 1

        for animation_name in animation:
            _, frames = animation[animation_name]

            furthest_extent: Optional[cbp.Box] = None
            images = []
            cropped_images = []
            for frame in frames:
                box = (
                    frame.box.x,
                    frame.box.y,
                    frame.box.x + frame.box.width,
                    frame.box.y + frame.box.height,
                )
                cropped_image = source_image.crop(box)
                cropped_images.append(cropped_image)

                content_box = cropped_image.getbbox()
                assert content_box is not None

                furthest_extent = expand_box_to_include(
                    furthest_extent,
                    cbp.Box(
                        content_box[0],
                        content_box[1],
                        content_box[2] - content_box[0],
                        content_box[3] - content_box[1],
                    ),
                )

            assert furthest_extent is not None

            for image in cropped_images:
                box = (
                    furthest_extent.x,
                    furthest_extent.y,
                    furthest_extent.x + furthest_extent.width,
                    furthest_extent.y + furthest_extent.height,
                )
                cropped_image = image.crop(box) if args.crop else image
                images.append(cropped_image)

            animation_filepath = (
                output_directory
                / f"{monster_name}_{seen_monster_names[monster_name] - 1}_{animation_name}.gif"
            )
            images[0].save(
                animation_filepath,
                save_all=True,
                append_images=images[1:],
                optimize=False,
                duration=100,
                loop=0,
                disposal=2,  # Avoids issues with transparency leading to frame bleeding
            )
            print(f"Wrote animation to: {animation_filepath}")

    return SUCCESS


def expand_box_to_include(box_a: Optional[cbp.Box], box_b: cbp.Box) -> cbp.Box:
    if box_a is None:
        return box_b

    left = min(box_a.x, box_b.x)
    top = min(box_a.y, box_a.y)

    right = max(box_a.x + box_a.width, box_b.x + box_b.width)
    bottom = max(box_a.y + box_a.height, box_b.y + box_b.height)

    assert left < right
    assert top < bottom

    return cbp.Box(
        left,
        top,
        right - left,
        bottom - top,
    )


def main_without_args() -> int:
    return main(sys.argv[1:])
