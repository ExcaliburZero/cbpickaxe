# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from typing import DefaultDict, List

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

            assert len(frames) > 0

            images = []
            cropped_images = []
            combined_image = None
            for frame in frames:
                box = (
                    frame.box.x,
                    frame.box.y,
                    frame.box.x + frame.box.width,
                    frame.box.y + frame.box.height,
                )
                cropped_image = source_image.crop(box)
                cropped_images.append(cropped_image)

                if combined_image is None:
                    combined_image = cropped_image.copy()
                else:
                    combined_image.paste(cropped_image, (0, 0), mask=cropped_image)

            assert combined_image is not None

            for image in cropped_images:
                cropped_image = (
                    image.crop(combined_image.getbbox()) if args.crop else image
                )
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


def main_without_args() -> int:
    return main(sys.argv[1:])
