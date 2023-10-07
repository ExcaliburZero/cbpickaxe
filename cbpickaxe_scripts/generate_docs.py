# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import Any, cast, Dict, IO, List

import argparse
import logging
import os
import pathlib
import shutil
import sys
import tomllib

import jinja2 as j2
import PIL.Image

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1

SOURCE_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = SOURCE_DIR / "templates"
MONSTER_FORM_TEMPLATE = TEMPLATES_DIR / "monster_form.html.template"

OFFICIAL_MONSTER_FORM_PATHS = [
    "res://data/monster_forms/",
    "res://data/monster_forms_secret/",
]
OFFICIAL_MOVE_PATHS = ["res://data/battle_moves/"]


@dataclass
class MonsterForms:
    paths: List[str]

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "MonsterForms":
        paths = d.get("paths", [])

        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, str)
        paths = cast(List[str], paths)

        return MonsterForms(paths)


@dataclass
class Moves:
    paths: List[str]

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Moves":
        paths = d.get("paths", [])

        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, str)
        paths = cast(List[str], paths)

        return Moves(paths)


@dataclass
class Config:
    output_directory: pathlib.Path
    roots: Dict[str, pathlib.Path]
    monster_forms: MonsterForms
    moves: Moves

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        output_directory = d.get("output_directory", "docs")
        roots = d["roots"]
        monster_forms_entry = d.get("monster_forms", {})
        moves_entry = d.get("moves", {})

        assert isinstance(output_directory, str)

        assert isinstance(roots, dict)
        for key, value in roots.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
        roots = cast(Dict[str, str], roots)

        assert isinstance(monster_forms_entry, dict)
        assert isinstance(moves_entry, dict)

        if "cassette_beasts" not in roots:
            logging.error('roots must contain "cassette_beasts"')
            raise ValueError()

        monster_forms = MonsterForms.from_dict(monster_forms_entry)
        moves = Moves.from_dict(moves_entry)

        return Config(
            output_directory=pathlib.Path(output_directory),
            roots={key: pathlib.Path(value) for key, value in roots.items()},
            monster_forms=monster_forms,
            moves=moves,
        )


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", nargs="+", default="docs.toml")

    args = parser.parse_args(argv)

    with open(args.config, "rb") as input_stream:
        try:
            config = Config.from_dict(tomllib.load(input_stream))
        except ValueError:
            logging.error("Failed to load configration file. See error(s) above.")
            return FAILURE

    env = j2.Environment(
        loader=j2.PackageLoader("cbpickaxe_scripts"), autoescape=j2.select_autoescape()
    )
    monster_form_template = env.get_template("monster_form.html")

    if config.output_directory.exists():
        shutil.rmtree(config.output_directory)
    config.output_directory.mkdir()

    hoylake = cbp.Hoylake()
    for name, root in config.roots.items():
        hoylake.load_root(name, pathlib.Path(root))

    for monsters_path in OFFICIAL_MONSTER_FORM_PATHS + config.monster_forms.paths:
        if monsters_path.endswith(".tres"):
            monster_forms = {monsters_path: hoylake.load_monster_form(monsters_path)}
        else:
            monster_forms = hoylake.load_monster_forms(monsters_path)

    for moves_path in OFFICIAL_MOVE_PATHS + config.moves.paths:
        _ = hoylake.load_moves(moves_path)

    monster_forms_dir = config.output_directory / "monsters"
    monster_forms_dir.mkdir()

    monster_form_images_dir = monster_forms_dir / "sprites"
    monster_form_images_dir.mkdir()

    monster_path, (_, monster_form) = sorted(monster_forms.items())[0]
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

    try:
        monster_sprite_filepath = get_idle_frame(
            monster_form, hoylake, images_dir
        ).relative_to(dest_dir)
    except ValueError:
        monster_sprite_filepath = None

    output_stream.write(
        template.render(
            name=hoylake.translate(monster_form.name),
            bestiary_index=f"{'-' if monster_form.bestiary_index < 0 else ''}{abs(monster_form.bestiary_index):03d}",
            monster_sprite_path=""
            if monster_sprite_filepath is None
            else monster_sprite_filepath,
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
                    for path, (_, move) in compatible_moves.items()
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
    try:
        animation = hoylake.load_animation(monster_form.battle_sprite_path)
    except ValueError:
        logging.warning(
            f"Could not find animation JSON file at path: {monster_form.battle_sprite_path}"
        )
        raise

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
