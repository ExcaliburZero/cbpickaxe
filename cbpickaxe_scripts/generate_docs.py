from typing import IO, List

import argparse
import os
import pathlib
import shutil
import sys

import jinja2 as j2
import PIL.Image

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1

SOURCE_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = SOURCE_DIR / "templates"
MONSTER_FORM_TEMPLATE = TEMPLATES_DIR / "monster_form.html.template"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument(
        "--move_paths",
        nargs="+",
        default=["res://data/battle_moves/"],
    )
    parser.add_argument(
        "--monster_form_paths",
        nargs="+",
        default=[
            "res://data/monster_forms/",
            "res://data/monster_forms_secret/",
            "res://mods/de_example_monster/traffikrabdos.tres",
        ],
    )
    parser.add_argument("--output_directory", default="docs")

    args = parser.parse_args(argv)

    env = j2.Environment(
        loader=j2.PackageLoader("cbpickaxe_scripts"), autoescape=j2.select_autoescape()
    )
    monster_form_template = env.get_template("monster_form.html")

    output_directory = pathlib.Path(args.output_directory)
    if output_directory.exists():
        shutil.rmtree(output_directory)
    output_directory.mkdir()

    hoylake = cbp.Hoylake()
    for root in args.roots:
        hoylake.load_root(pathlib.Path(root))

    for monsters_path in args.monster_form_paths:
        if monsters_path.endswith(".tres"):
            monster_forms = {monsters_path: hoylake.load_monster_form(monsters_path)}
        else:
            monster_forms = hoylake.load_monster_forms(monsters_path)

    for moves_path in args.move_paths:
        _ = hoylake.load_moves(moves_path)

    monster_forms_dir = output_directory / "monsters"
    monster_forms_dir.mkdir()

    monster_form_images_dir = monster_forms_dir / "sprites"
    monster_form_images_dir.mkdir()

    monster_path, monster_form = sorted(monster_forms.items())[0]
    monster_page_filepath = monster_forms_dir / (
        hoylake.translate(monster_form.name) + ".html"
    )
    with open(monster_page_filepath, "w", encoding="utf-8") as output_stream:
        create_monster_form_page(
            monster_path,
            monster_form,
            hoylake,
            monster_form_template,
            monster_forms_dir,
            monster_form_images_dir,
            output_stream,
        )

    return SUCCESS


def create_monster_form_page(
    path: str,
    monster_form: cbp.MonsterForm,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    dest_dir: pathlib.Path,
    images_dir: pathlib.Path,
    output_stream: IO[str],
) -> None:
    compatible_moves = hoylake.get_moves_by_tags(monster_form.move_tags + ["any"])

    monster_sprite_filepath = get_idle_frame(
        monster_form, hoylake, images_dir
    ).relative_to(dest_dir)

    output_stream.write(
        template.render(
            name=hoylake.translate(monster_form.name),
            bestiary_index=f"{monster_form.bestiary_index:03}",
            monster_sprite_path=monster_sprite_filepath,
            description=hoylake.translate(monster_form.description),
            elemental_type=monster_form.elemental_types[0].capitalize(),
            bestiary_bio_1=hoylake.translate(monster_form.bestiary_bios[0]),
            bestiary_bio_2=hoylake.translate(monster_form.bestiary_bios[1]),
            max_hp=monster_form.max_hp,
            melee_attack=monster_form.melee_attack,
            melee_defense=monster_form.melee_defense,
            ranged_attack=monster_form.ranged_attack,
            ranged_defense=monster_form.ranged_defense,
            speed=monster_form.speed,
            stat_total=monster_form.max_hp
            + monster_form.melee_attack
            + monster_form.melee_defense
            + monster_form.ranged_attack
            + monster_form.ranged_defense
            + monster_form.speed,
            max_ap=monster_form.max_ap,
            move_slots=f"{monster_form.move_slots} - {monster_form.max_move_slots}",
            compatible_moves=sorted(
                [
                    {
                        "name": hoylake.translate(move.name),
                        "type": move.elemental_types[0].capitalize()
                        if len(move.elemental_types) > 0
                        else "Typeless",
                        "category": hoylake.translate(move.category_name),
                        "power": move.power if move.power > 0 else "—",
                        "accuracy": "Unavoidable"
                        if move.unavoidable
                        else move.accuracy,
                        "cost": "Passive"
                        if move.is_passive_only
                        else f"{move.cost} AP",
                    }
                    for path, move in compatible_moves.items()
                ],
                key=lambda m: m["name"],
            ),
        )
    )


def get_idle_frame(
    monster_form: cbp.MonsterForm,
    hoylake: cbp.Hoylake,
    images_dir: pathlib.Path,
) -> pathlib.Path:
    animation = hoylake.load_animation(monster_form.battle_sprite_path)
    frame_box = animation.get_frame("idle", 0).box

    image_filepath_relative = (
        "/".join(monster_form.battle_sprite_path.split("/")[:-1])
        + "/"
        + animation.image
    )

    image_filepath = hoylake.lookup_filepath(image_filepath_relative)
    source_image = PIL.Image.open(image_filepath)

    box = (
        frame_box.x,
        frame_box.y,
        frame_box.x + frame_box.width,
        frame_box.y + frame_box.height,
    )
    cropped_image = source_image.crop(box)

    output_filepath = images_dir / (hoylake.translate(monster_form.name) + ".png")
    cropped_image.save(output_filepath)

    return output_filepath


def main_without_args() -> int:
    return main(sys.argv[1:])
