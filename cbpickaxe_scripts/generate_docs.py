# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import Any, cast, Dict, IO, List, Optional, Tuple

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
OFFICIAL_ITEMS_PATHS = ["res://data/items/"]


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
class Items:
    paths: List[str]
    include_official: bool

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> "Items":
        paths = d.get("paths", [])
        include_official = d.get("include_official", False)

        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, str)
        paths = cast(List[str], paths)

        return Items(paths=paths, include_official=include_official)


@dataclass
class Config:
    output_directory: pathlib.Path
    roots: Dict[str, pathlib.Path]
    monster_forms: MonsterForms
    moves: Moves
    items: Items

    @property
    def monster_forms_dir(self) -> pathlib.Path:
        return self.output_directory / "monsters"

    @property
    def moves_dir(self) -> pathlib.Path:
        return self.output_directory / "moves"

    @property
    def items_dir(self) -> pathlib.Path:
        return self.output_directory / "items"

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        output_directory = d.get("output_directory", "docs")
        roots = d["roots"]
        monster_forms_entry = d.get("monster_forms", {})
        moves_entry = d.get("moves", {})
        items_entry = d.get("items", {})

        assert isinstance(output_directory, str)

        assert isinstance(roots, dict)
        for key, value in roots.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
        roots = cast(Dict[str, str], roots)

        assert isinstance(monster_forms_entry, dict)
        assert isinstance(moves_entry, dict)
        assert isinstance(items_entry, dict)

        if OFFICIAL_ROOT_NAME not in roots:
            logging.error(f'roots must contain "{OFFICIAL_ROOT_NAME}"')
            raise ValueError()

        monster_forms = MonsterForms.from_dict(monster_forms_entry)
        moves = Moves.from_dict(moves_entry)
        items = Items.from_dict(items_entry)

        return Config(
            output_directory=pathlib.Path(output_directory),
            roots={key: pathlib.Path(value) for key, value in roots.items()},
            monster_forms=monster_forms,
            moves=moves,
            items=items,
        )


@dataclass
class Root:
    name: str
    has_moves: bool
    has_monsters: bool
    has_items: bool


def main(argv: List[str]) -> int:
    logging.basicConfig(level=logging.WARN, format="%(levelname)s> %(message)s")

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", description="Build the documentation for the mod."
    )
    build_parser.add_argument("--config", default="docs.toml")
    build_parser.add_argument("--locale", default="en")

    _ = subparsers.add_parser(
        "new", description="Create a configuration file for the mod's documentation."
    )

    args = parser.parse_args(argv)

    if args.command == "new":
        return create_new_config(pathlib.Path("docs.toml"))
    elif args.command == "build":
        return build_documentation(pathlib.Path(args.config), args.locale)
    else:
        logging.error(f"Unrecognized command: {args.command}")
        return FAILURE


def build_documentation(config_filepath: pathlib.Path, locale: str) -> int:
    if not pathlib.Path(config_filepath).exists():
        logging.error(
            f"Could not find documentation configuration file: {config_filepath}"
        )
        logging.error(
            "If you do not already have one, you should run `cbpickaxe_generate_docs new` to create one."
        )
        return FAILURE

    with open(config_filepath, "rb") as input_stream:
        toml_data = tomllib.load(input_stream)
        try:
            config = Config.from_dict(toml_data)
        except ValueError:
            logging.error("Failed to load configration file. See error(s) above.")
            return FAILURE

    env = j2.Environment(
        loader=j2.PackageLoader("cbpickaxe_scripts"),
        autoescape=j2.select_autoescape(),
    )
    monster_form_template = env.get_template("monster_form.html")
    move_template = env.get_template("move.html")
    item_template = env.get_template("item.html")
    index_template = env.get_template("index.html")

    if config.output_directory.exists():
        shutil.rmtree(config.output_directory)
    config.output_directory.mkdir()

    hoylake = cbp.Hoylake(default_locale=locale)
    for name, root in config.roots.items():
        hoylake.load_root(name, pathlib.Path(root))

    monster_forms = load_monster_forms(config, hoylake)
    moves = load_moves(config, hoylake)
    items = load_items(config, hoylake)

    copy_item_images(config, hoylake, items)

    roots = generate_index_page(
        config, hoylake, index_template, monster_forms, moves, items
    )
    generate_monster_form_pages(
        config, hoylake, monster_form_template, monster_forms, roots
    )
    generate_move_pages(config, hoylake, move_template, moves, roots)
    generate_item_pages(config, hoylake, item_template, items, roots)

    return SUCCESS


def create_new_config(config_filepath: pathlib.Path) -> int:
    if config_filepath.exists():
        overwrite = input(
            f'There is already a documentation config file at "{config_filepath}". Would you like to overwrite it? [y/n]: '
        ).lower()

        if overwrite not in {"y", "yes"}:
            return FAILURE

    current_dir_name = pathlib.Path().absolute().name

    mod_name = input("Enter the name of your mod (no spaces, underscores allowed): ")
    has_monsters_str = input(
        "Does your mod add any new monster species [y/n]: "
    ).lower()
    has_moves_str = input("Does your mod add any new moves/stickers [y/n]: ").lower()
    cassette_beasts_path = input(
        "Enter the path to your decompiled copy of Cassette Beasts: "
    )

    cassette_beasts_path = cassette_beasts_path.replace('"', "")

    if mod_name == "":
        mod_name = current_dir_name
    if has_monsters_str == "":
        has_monsters_str = "n"
    if has_moves_str == "":
        has_moves_str = "n"

    has_monsters = has_monsters_str in {"y", "yes"}
    has_moves = has_moves_str in {"y", "yes"}

    with open(config_filepath, "w", encoding="utf-8") as output_stream:
        output_stream.write('output_directory = "docs"\n')
        output_stream.write("\n")

        output_stream.write("[roots]\n")
        output_stream.write(f'{OFFICIAL_ROOT_NAME} = "{cassette_beasts_path}"\n')
        output_stream.write(f'{mod_name} = "."\n')
        output_stream.write("\n")

        if has_monsters:
            output_stream.write("[monster_forms]\n")
            output_stream.write(
                'paths = [\n   "res://mods/my_mod/my_monsters/" # TODO: replace with the \'res://...\' path to the folder where you keep the monster_form ".tres" files\n]\n'
            )
            output_stream.write("\n")

        if has_moves:
            output_stream.write("[moves]\n")
            output_stream.write(
                'paths = [\n   "res://mods/my_mod/my_moves/" # TODO: replace with the \'res://...\' path to the folder where you keep the move ".tres" files\n]\n'
            )
            output_stream.write("\n")

    print("===========================")
    print("Successfully generated configuration file:", config_filepath)
    print(
        "Edit it in a text editor to fill in any remaining fields (ex. monster form and move paths)"
    )

    return SUCCESS


def copy_item_images(
    config: Config, hoylake: cbp.Hoylake, items: Dict[str, Tuple[str, cbp.Item]]
) -> None:
    for _, (root_name, item) in items.items():
        if not config.items.include_official and root_name == OFFICIAL_ROOT_NAME:
            continue

        config.items_dir.mkdir(exist_ok=True)

        item_icons_dir = config.items_dir / "icons"
        item_icons_dir.mkdir(exist_ok=True)

        for _, (_, item) in items.items():
            if item.icon is None:
                continue

            source_path = hoylake.lookup_filepath(item.icon)
            dest_path = item_icons_dir / source_path.name

            shutil.copy(source_path, dest_path)


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


def load_items(config: Config, hoylake: cbp.Hoylake) -> Dict[str, Tuple[str, cbp.Item]]:
    items = {}
    for items_path in OFFICIAL_ITEMS_PATHS + config.items.paths:
        if items_path.endswith(".tres"):
            items[items_path] = hoylake.load_item(items_path)
        else:
            items.update(hoylake.load_items(items_path))

    return items


def generate_index_page(
    config: Config,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    monster_forms: Dict[str, Tuple[str, cbp.MonsterForm]],
    moves: Dict[str, Tuple[str, cbp.Move]],
    items: Dict[str, Tuple[str, cbp.Item]],
) -> List[Root]:
    index_filepath = config.output_directory / "index.html"
    with open(index_filepath, "w", encoding="utf-8") as output_stream:
        return create_index_page(
            config, hoylake, template, monster_forms, moves, items, output_stream
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
                root_name,
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
    roots: List[Root],
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
                root_name,
                move,
                hoylake,
                move_template,
                roots,
                output_stream,
            )


def generate_item_pages(
    config: Config,
    hoylake: cbp.Hoylake,
    item_template: j2.Template,
    items: Dict[str, Tuple[str, cbp.Item]],
    roots: List[Root],
) -> None:
    for item_path, (root_name, item) in items.items():
        if not config.items.include_official and root_name == OFFICIAL_ROOT_NAME:
            continue

        config.items_dir.mkdir(exist_ok=True)

        item_page_filepath = config.items_dir / (hoylake.translate(item.name) + ".html")
        with open(item_page_filepath, "w", encoding="utf-8") as output_stream:
            create_item_page(
                config,
                item_path,
                root_name,
                item,
                hoylake,
                item_template,
                roots,
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
    monster_root: str,
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
            title=hoylake.translate(monster_form.name),
            name=hoylake.translate(monster_form.name),
            bestiary_index=f"{'-' if monster_form.bestiary_index < 0 else ''}{abs(monster_form.bestiary_index):03d}",
            monster_root=monster_root,
            monster_root_link=str(
                special_relative_to(
                    config.monster_forms_dir,
                    config.output_directory / "index.html",
                    config.output_directory,
                )
            )
            + f"#{monster_root}",
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
                        "items_o": [True] if root.has_items else [],
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
                key=lambda d: (d["name"] == OFFICIAL_ROOT_NAME, d["name"]),
            ),
        )
    )


def create_move_page(
    config: Config,
    _path: str,
    move_root: str,
    move: cbp.Move,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    roots: List[Root],
    output_stream: IO[str],
) -> None:
    compatible_monsters = hoylake.get_monster_forms_by_tags(move.tags)

    output_stream.write(
        template.render(
            title=hoylake.translate(move.name),
            name=hoylake.translate(move.name),
            move_root=move_root,
            move_root_link=str(
                special_relative_to(
                    config.monster_forms_dir,
                    config.output_directory / "index.html",
                    config.output_directory,
                )
            )
            + f"#{move_root}",
            elemental_type=move.elemental_types[0].capitalize()
            if len(move.elemental_types) > 0
            else "Typeless",
            description=hoylake.translate(move.description),
            category=hoylake.translate(move.category_name),
            power=move.power,
            accuracy=move.accuracy,
            targets=move.target_type.to_name(),
            num_hits=move.min_hits
            if move.min_hits == move.max_hits
            else f"{move.min_hits} - {move.max_hits}",
            use_cost="" if move.is_passive_only else f"{move.cost} AP",
            copyable="Yes" if move.can_be_copied else "No",
            priority=str(move.priority),
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
            roots=sorted(
                [
                    {
                        "name": root.name,
                        "monsters": [True] if root.has_monsters else [],
                        "moves": [True] if root.has_moves else [],
                        "items_o": [True] if root.has_items else [],
                        "root_link": str(
                            special_relative_to(
                                config.moves_dir,
                                config.output_directory / "index.html",
                                config.output_directory,
                            )
                        )
                        + f"#{root.name}",
                    }
                    for root in roots
                ],
                key=lambda d: (d["name"] == OFFICIAL_ROOT_NAME, d["name"]),
            ),
        )
    )


def create_item_page(
    config: Config,
    _path: str,
    item_root: str,
    item: cbp.Item,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    roots: List[Root],
    output_stream: IO[str],
) -> None:
    icon_path = get_item_icon_path(config, hoylake, item)

    output_stream.write(
        template.render(
            title=hoylake.translate(item.name),
            name=hoylake.translate(item.name),
            description=hoylake.translate(item.description),
            category=item.category,
            item_root=item_root,
            item_root_link=str(
                special_relative_to(
                    config.items_dir,
                    config.output_directory / "index.html",
                    config.output_directory,
                )
            )
            + f"#{item_root}",
            icon=special_relative_to(
                config.items_dir,
                config.output_directory / icon_path,
                config.items_dir,
            )
            if icon_path is not None
            else "",
            roots=sorted(
                [
                    {
                        "name": root.name,
                        "monsters": [True] if root.has_monsters else [],
                        "moves": [True] if root.has_moves else [],
                        "items_o": [True] if root.has_items else [],
                        "root_link": str(
                            special_relative_to(
                                config.moves_dir,
                                config.output_directory / "index.html",
                                config.output_directory,
                            )
                        )
                        + f"#{root.name}",
                    }
                    for root in roots
                ],
                key=lambda d: (d["name"] == OFFICIAL_ROOT_NAME, d["name"]),
            ),
        )
    )


def create_index_page(
    config: Config,
    hoylake: cbp.Hoylake,
    template: j2.Template,
    monster_forms: Dict[str, Tuple[str, cbp.MonsterForm]],
    moves: Dict[str, Tuple[str, cbp.Move]],
    items: Dict[str, Tuple[str, cbp.Item]],
    output_stream: IO[str],
) -> List[Root]:
    roots = (
        {root for _, (root, _) in monster_forms.items()}
        | {root for _, (root, _) in moves.items()}
        | {root for _, (root, _) in items.items()}
    )
    if (
        not config.monster_forms.include_official
        and not config.moves.include_official
        and not config.items.include_official
    ):
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
            [
                (item_path, item_form)
                for item_path, (
                    item_root,
                    item_form,
                ) in items.items()
                if item_root == root
                and (config.items.include_official or item_root != OFFICIAL_ROOT_NAME)
            ],
        )
        for root in roots
    }

    list_of_roots = [
        Root(
            name=root_name,
            has_monsters=len(root_monsters) > 0,
            has_moves=len(root_moves) > 0,
            has_items=len(root_items) > 0,
        )
        for root_name, (root_monsters, root_moves, root_items) in data_by_root.items()
    ]

    current_dir = config.output_directory

    output_stream.write(
        template.render(
            title="Mod Documentation",
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
                        "items_o": sorted(  # Note: extra "_o" is to avoid conflicting with the "items()" method
                            [
                                {
                                    "name": hoylake.translate(item.name),
                                    "category": item.category,
                                    "icon": get_item_icon_path(config, hoylake, item),
                                    "link": special_relative_to(
                                        config.output_directory,
                                        config.items_dir
                                        / (hoylake.translate(item.name) + ".html"),
                                        config.output_directory,
                                    ),
                                }
                                for _, item in root_items
                            ],
                            key=lambda d: (
                                cast(Dict[str, Any], d)[
                                    "name"
                                ],  # cast needed to avoid a mypy type inference bug
                            ),
                        ),
                    }
                    for root, (
                        root_monster_forms,
                        root_moves,
                        root_items,
                    ) in data_by_root.items()
                ],
                key=lambda d: (d["name"] == OFFICIAL_ROOT_NAME, d["name"]),
            ),
        )
    )

    return list_of_roots


def get_item_icon_path(
    config: Config, hoylake: cbp.Hoylake, item: cbp.Item
) -> Optional[pathlib.Path]:
    if item.icon is None:
        return None

    return special_relative_to(
        config.output_directory,
        config.items_dir / "icons" / hoylake.lookup_filepath(item.icon).name,
        config.output_directory,
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

    try:
        frame_box = animation.get_frame("idle", 0).box
    except KeyError as e:
        logging.warning(
            f"Found animation file, but could not find idle animation for: {monster_form.battle_sprite_path}"
        )
        raise ValueError() from e

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
