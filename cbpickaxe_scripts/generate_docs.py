# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import Any, cast, Dict, IO, List, Tuple

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

OFFICIAL_ROOT_NAME = "cassette_beasts"
OFFICIAL_MONSTER_FORM_PATHS = [
    "res://data/monster_forms/",
    "res://data/monster_forms_secret/",
]
OFFICIAL_MOVE_PATHS = ["res://data/battle_moves/"]


@dataclass
class MonsterForms:
    paths: List[str]
    include_official: bool

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "MonsterForms":
        paths = d.get("paths", [])
        include_official = d.get("include_official", False)

        assert isinstance(include_official, bool)

        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, str)
        paths = cast(List[str], paths)

        return MonsterForms(paths=paths, include_official=include_official)


@dataclass
class Moves:
    paths: List[str]
    include_official: bool

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Moves":
        paths = d.get("paths", [])
        include_official = d.get("include_official", False)

        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, str)
        paths = cast(List[str], paths)

        return Moves(paths=paths, include_official=include_official)


@dataclass
class Config:
    output_directory: pathlib.Path
    roots: Dict[str, pathlib.Path]
    monster_forms: MonsterForms
    moves: Moves

    @property
    def monster_forms_dir(self) -> pathlib.Path:
        return self.output_directory / "monsters"

    @property
    def moves_dir(self) -> pathlib.Path:
        return self.output_directory / "moves"

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

        if OFFICIAL_ROOT_NAME not in roots:
            logging.error(f'roots must contain "{OFFICIAL_ROOT_NAME}"')
            raise ValueError()

        monster_forms = MonsterForms.from_dict(monster_forms_entry)
        moves = Moves.from_dict(moves_entry)

        return Config(
            output_directory=pathlib.Path(output_directory),
            roots={key: pathlib.Path(value) for key, value in roots.items()},
            monster_forms=monster_forms,
            moves=moves,
        )


@dataclass
class Root:
    name: str
    has_moves: bool
    has_monsters: bool


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", nargs="+", default="docs.toml")
    parser.add_argument("--locale", default="en")

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
    move_template = env.get_template("move.html")
    index_template = env.get_template("index.html")

    if config.output_directory.exists():
        shutil.rmtree(config.output_directory)
    config.output_directory.mkdir()

    hoylake = cbp.Hoylake(default_locale=args.locale)
    for name, root in config.roots.items():
        hoylake.load_root(name, pathlib.Path(root))

    monster_forms = load_monster_forms(config, hoylake)
    moves = load_moves(config, hoylake)

    roots = generate_index_page(config, hoylake, index_template, monster_forms, moves)
    generate_monster_form_pages(
        config, hoylake, monster_form_template, monster_forms, roots
    )
    generate_move_pages(config, hoylake, move_template, moves)

    return SUCCESS


def load_monster_forms(
    config: Config, hoylake: cbp.Hoylake
) -> Dict[str, Tuple[str, cbp.MonsterForm]]:
    monster_forms = {}
    for monsters_path in OFFICIAL_MONSTER_FORM_PATHS + config.monster_forms.paths:
        if monsters_path.endswith(".tres"):
            monster_forms[monsters_path] = hoylake.load_monster_form(monsters_path)
        else:
            monster_forms.update(hoylake.load_monster_forms(monsters_path))

    return monster_forms


def load_moves(config: Config, hoylake: cbp.Hoylake) -> Dict[str, Tuple[str, cbp.Move]]:
    moves = {}
    for moves_path in OFFICIAL_MOVE_PATHS + config.moves.paths:
        if moves_path.endswith(".tres"):
            moves[moves_path] = hoylake.load_move(moves_path)
        else:
            moves.update(hoylake.load_moves(moves_path))

    return moves


def generate_index_page(
    config: Config,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    monster_forms: Dict[str, Tuple[str, cbp.MonsterForm]],
    moves: Dict[str, Tuple[str, cbp.Move]],
) -> List[Root]:
    index_filepath = config.output_directory / "index.html"
    with open(index_filepath, "w", encoding="utf-8") as output_stream:
        return create_index_page(
            config, hoylake, template, monster_forms, moves, output_stream
        )


def generate_monster_form_pages(
    config: Config,
    hoylake: cbp.Hoylake,
    monster_form_template: j2.Template,
    monster_forms: Dict[str, Tuple[str, cbp.MonsterForm]],
    roots: List[Root],
) -> None:
    for monster_path, (root_name, monster_form) in monster_forms.items():
        if (
            not config.monster_forms.include_official
            and root_name == OFFICIAL_ROOT_NAME
        ):
            continue

        config.monster_forms_dir.mkdir(exist_ok=True)

        monster_form_images_dir = config.monster_forms_dir / "sprites"
        monster_form_images_dir.mkdir(exist_ok=True)

        monster_page_filepath = config.monster_forms_dir / (
            hoylake.translate(monster_form.name) + ".html"
        )
        with open(monster_page_filepath, "w", encoding="utf-8") as output_stream:
            create_monster_form_page(
                config,
                monster_path,
                monster_form,
                hoylake,
                monster_form_template,
                config.monster_forms_dir,
                monster_form_images_dir,
                roots,
                output_stream,
            )


def generate_move_pages(
    config: Config,
    hoylake: cbp.Hoylake,
    move_template: j2.Template,
    moves: Dict[str, Tuple[str, cbp.Move]],
) -> None:
    for move_path, (root_name, move) in moves.items():
        if not config.moves.include_official and root_name == OFFICIAL_ROOT_NAME:
            continue

        config.moves_dir.mkdir(exist_ok=True)

        move_page_filepath = config.moves_dir / (hoylake.translate(move.name) + ".html")
        with open(move_page_filepath, "w", encoding="utf-8") as output_stream:
            create_move_page(
                config,
                move_path,
                move,
                hoylake,
                move_template,
                output_stream,
            )


def get_move_link(
    config: Config,
    hoylake: cbp.Hoylake,
    root_name: str,
    move: cbp.Move,
    current_dir: pathlib.Path,
) -> str:
    if root_name == OFFICIAL_ROOT_NAME and not config.moves.include_official:
        move_name = hoylake.translate(move.name)
        return f"https://wiki.cassettebeasts.com/wiki/{move_name.replace(' ', '_')}"

    move_filepath = config.moves_dir / (hoylake.translate(move.name) + ".html")

    return str(special_relative_to(current_dir, move_filepath, config.output_directory))


def get_monster_form_link(
    config: Config,
    hoylake: cbp.Hoylake,
    root_name: str,
    monster_form: cbp.MonsterForm,
    current_dir: pathlib.Path,
) -> str:
    if root_name == OFFICIAL_ROOT_NAME and not config.monster_forms.include_official:
        move_name = hoylake.translate(monster_form.name)
        return f"https://wiki.cassettebeasts.com/wiki/{move_name.replace(' ', '_')}"

    monster_filepath = config.monster_forms_dir / (
        hoylake.translate(monster_form.name) + ".html"
    )

    return str(
        special_relative_to(current_dir, monster_filepath, config.output_directory)
    )


def special_relative_to(
    source_dir: pathlib.Path, dest_filepath: pathlib.Path, root: pathlib.Path
) -> pathlib.Path:
    num_times_to_go_up = len(source_dir.relative_to(root).parts)

    filepath = dest_filepath.relative_to(root)

    backs = pathlib.Path()
    for _ in range(0, num_times_to_go_up):
        backs = pathlib.Path("..") / backs

    return backs / filepath


def create_monster_form_page(
    config: Config,
    _path: str,
    monster_form: cbp.MonsterForm,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    dest_dir: pathlib.Path,
    images_dir: pathlib.Path,
    roots: List[Root],
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
            elemental_type=monster_form.elemental_types[0].capitalize()
            if len(monster_form.elemental_types) > 0
            else "Typeless",
            bestiary_bio_1=hoylake.translate(monster_form.bestiary_bios[0])
            if len(monster_form.bestiary_bios) > 0
            else "",
            bestiary_bio_2=hoylake.translate(monster_form.bestiary_bios[1])
            if len(monster_form.bestiary_bios) > 1
            else "",
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
                        "link": get_move_link(
                            config, hoylake, move_root, move, config.moves_dir
                        ),
                    }
                    for path, (move_root, move) in compatible_moves.items()
                ],
                key=lambda m: m["name"],
            ),
            roots=sorted(
                [
                    {
                        "name": root.name,
                        "monsters": [True] if root.has_monsters else [],
                        "moves": [True] if root.has_moves else [],
                        "root_link": str(
                            special_relative_to(
                                config.monster_forms_dir,
                                config.output_directory / "index.html",
                                config.output_directory,
                            )
                        )
                        + f"#{root.name}",
                    }
                    for root in roots
                ],
                key=lambda d: d["name"],
            ),
        )
    )


def create_move_page(
    config: Config,
    _path: str,
    move: cbp.Move,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    output_stream: IO[str],
) -> None:
    compatible_monsters = hoylake.get_monster_forms_by_tags(move.tags)

    output_stream.write(
        template.render(
            name=hoylake.translate(move.name),
            elemental_type=move.elemental_types[0].capitalize()
            if len(move.elemental_types) > 0
            else "Typeless",
            description=hoylake.translate(move.description),
            compatible_monsters=sorted(
                [
                    {
                        "name": hoylake.translate(monster_form.name),
                        "bestiary_index": f"{'-' if monster_form.bestiary_index < 0 else ''}{abs(monster_form.bestiary_index):03d}",
                        "bestiary_index_raw": monster_form.bestiary_index,
                        "type": monster_form.elemental_types[0].capitalize()
                        if len(monster_form.elemental_types) > 0
                        else "Typeless",
                        "link": get_monster_form_link(
                            config,
                            hoylake,
                            monster_root,
                            monster_form,
                            config.moves_dir,
                        ),
                    }
                    for _, (monster_root, monster_form) in compatible_monsters.items()
                ],
                key=lambda d: (d["bestiary_index_raw"], d["name"]),
            ),
        )
    )


def create_index_page(
    config: Config,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    monster_forms: Dict[str, Tuple[str, cbp.MonsterForm]],
    moves: Dict[str, Tuple[str, cbp.Move]],
    output_stream: IO[str],
) -> List[Root]:
    roots = {root for _, (root, _) in monster_forms.items()} | {
        root for _, (root, _) in moves.items()
    }
    if not config.monster_forms.include_official and not config.moves.include_official:
        roots.discard(OFFICIAL_ROOT_NAME)

    data_by_root = {
        root: (
            [
                (monster_path, monster_form)
                for monster_path, (
                    monster_root,
                    monster_form,
                ) in monster_forms.items()
                if monster_root == root
                and (
                    config.monster_forms.include_official
                    or monster_root != OFFICIAL_ROOT_NAME
                )
            ],
            [
                (move_path, move_form)
                for move_path, (
                    move_root,
                    move_form,
                ) in moves.items()
                if move_root == root
                and (config.moves.include_official or move_root != OFFICIAL_ROOT_NAME)
            ],
        )
        for root in roots
    }

    list_of_roots = [
        Root(
            name=root_name,
            has_monsters=len(root_monsters) > 0,
            has_moves=len(root_moves) > 0,
        )
        for root_name, (root_monsters, root_moves) in data_by_root.items()
    ]

    current_dir = config.output_directory

    output_stream.write(
        template.render(
            roots=sorted(
                [
                    {
                        "name": root,
                        "root_link": str(
                            special_relative_to(
                                current_dir,
                                config.output_directory / "index.html",
                                config.output_directory,
                            )
                        )
                        + f"#{root}",
                        "monsters": sorted(
                            [
                                {
                                    "name": hoylake.translate(monster_form.name),
                                    "bestiary_index": f"{'-' if monster_form.bestiary_index < 0 else ''}{abs(monster_form.bestiary_index):03d}",
                                    "bestiary_index_raw": monster_form.bestiary_index,
                                    "type": monster_form.elemental_types[0].capitalize()
                                    if len(monster_form.elemental_types) > 0
                                    else "Typeless",
                                    "link": get_monster_form_link(
                                        config,
                                        hoylake,
                                        root,
                                        monster_form,
                                        config.output_directory,
                                    ),
                                }
                                for _, monster_form in root_monster_forms
                            ],
                            key=lambda d: (
                                cast(Dict[str, Any], d)[
                                    "bestiary_index_raw"
                                ],  # casts needed to avoid a mypy type inference bug
                                cast(Dict[str, Any], d)["name"],
                            ),
                        ),
                        "moves": sorted(
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
                                    "link": get_move_link(
                                        config,
                                        hoylake,
                                        root,
                                        move,
                                        config.output_directory,
                                    ),
                                }
                                for _, move in root_moves
                            ],
                            key=lambda d: (
                                cast(Dict[str, Any], d)[
                                    "name"
                                ],  # cast needed to avoid a mypy type inference bug
                            ),
                        ),
                    }
                    for root, (root_monster_forms, root_moves) in data_by_root.items()
                ],
                key=lambda d: (d["name"] == OFFICIAL_ROOT_NAME, d["name"]),
            )
        )
    )

    return list_of_roots


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
