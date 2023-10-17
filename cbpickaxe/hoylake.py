"""
Code for loading in data files and querying data from them.
"""
from typing import Dict, List, Iterable, Optional, Set, Tuple

import collections
import json
import logging
import os
import pathlib
import re

from .animation import Animation
from .item import Item
from .monster_form import MonsterForm
from .move import Move
from .translation_table import TranslationTable

RelativeResPath = pathlib.Path
RootName = str


class Hoylake:
    """
    A class that handles loading in data files from the decompiled game.
    """

    def __init__(self, default_locale: Optional[str] = None) -> None:
        self.__roots: Dict[str, pathlib.Path] = {}
        self.__translation_tables: collections.defaultdict[
            str, List[TranslationTable]
        ] = collections.defaultdict(lambda: [])

        self.__default_locale = default_locale if default_locale is not None else "en"

        self.__monster_forms: Dict[RelativeResPath, Tuple[RootName, MonsterForm]] = {}
        self.__moves: Dict[RelativeResPath, Tuple[RootName, Move]] = {}
        self.__animations: Dict[RelativeResPath, Tuple[RootName, Animation]] = {}
        self.__items: Dict[RelativeResPath, Tuple[RootName, Item]] = {}

        self.__moves_to_ignore = ["res://data/battle_moves/placeholder.tres"]

    def load_root(self, name: str, new_root: str | os.PathLike) -> None:
        """
        Adds the given root directory to the list of known root directories.

        Can be called multiple times in order to load multiple root directories
        (ex. base game, DLC, mods).

        Must be run at least once before loading in any files (ex. monster forms).
        """
        if not isinstance(new_root, pathlib.Path):
            new_root = pathlib.Path(new_root)

        logging.debug(f"Loading new root directory: {new_root}")

        if name in self.__roots:
            raise ValueError(f"A root with name {name} has already been loaded.")

        self.__roots[name] = new_root
        self.__load_translation_tables(new_root)

    def load_animation(self, path: str) -> Animation:
        """
        Loads in the animation at the given res:// filepath.

        Must have loaded at least one root before running.

        If there is no animation file at that location in any of the loaded root directories,
        then a ValueError will be raised.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        if relative_path in self.__animations:
            return self.__animations[relative_path][1]

        for root_name, root in self.__roots.items():
            animation_path = root / relative_path
            animation_import_path = pathlib.Path(
                str((root / relative_path)) + ".import"
            )
            if animation_path.exists():
                with open(animation_path, "r", encoding="utf-8") as input_stream:
                    animation = Animation.from_dict(json.load(input_stream))
                    self.__animations[relative_path] = (root_name, animation)

                    return animation
            elif animation_import_path.exists():
                # If the original JSON animation file is not available (since it was compiled and
                # the original was not distributed), then lookup the `.import` version which will
                # point to the compiled `.scn` version fo the file which we can parse to get out
                # the information we need.
                import_path = None
                with open(animation_import_path, "r", encoding="utf-8") as input_stream:
                    for line in input_stream:
                        match = re.match(r'path="(res.+)"', line)
                        if match is not None:
                            import_path = match.groups()[0]

                assert import_path is not None
                with open(self.lookup_filepath(import_path), "rb") as input_stream:
                    animation = Animation.from_scn(input_stream)
                    self.__animations[relative_path] = (root_name, animation)

                    return animation

        raise ValueError(f"Could not find animation file at path: {path}")

    def load_monster_form(self, path: str) -> Tuple[RootName, MonsterForm]:
        """
        Loads in the monster form at the given res:// filepath.

        Must have loaded at least one root before running.

        If there is no monster form file at that location in any of the loaded root directories,
        then a ValueError will be raised.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        if relative_path in self.__monster_forms:
            return self.__monster_forms[relative_path]

        for root_name, root in self.__roots.items():
            monster_path = root / relative_path
            if monster_path.exists():
                with open(monster_path, "r", encoding="utf-8") as input_stream:
                    monster_form = MonsterForm.from_tres(input_stream)
                    self.__monster_forms[relative_path] = (root_name, monster_form)

                    return (root_name, monster_form)

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_monster_forms(self, path: str) -> Dict[str, Tuple[RootName, MonsterForm]]:
        """
        Loads in all of the monster forms within the given res:// directory path.

        Looks for that path in all of the loaded root directories.

        Must have loaded at least one root before running.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        monster_forms: Dict[str, Tuple[RootName, MonsterForm]] = {}
        for root_name, root in self.__roots.items():
            monsters_dir_path = root / relative_path
            if monsters_dir_path.exists():
                monster_paths = sorted(monsters_dir_path.glob("*.tres"))
                for monster_path in monster_paths:
                    monster_relative_path = relative_path / monster_path.name

                    if monster_relative_path in self.__monster_forms:
                        monster_forms[
                            f"res://{monster_relative_path}"
                        ] = self.__monster_forms[monster_relative_path]
                        continue

                    with open(monster_path, "r", encoding="utf-8") as input_stream:
                        monster_form = MonsterForm.from_tres(input_stream)

                        monster_relative_path = relative_path / monster_path.name
                        monster_forms[f"res://{monster_relative_path}"] = (
                            root_name,
                            monster_form,
                        )
                        self.__monster_forms[monster_relative_path] = (
                            root_name,
                            monster_form,
                        )

        return monster_forms

    def load_move(self, path: str) -> Tuple[RootName, Move]:
        """
        Loads in the move at the given res:// filepath.

        Must have loaded at least one root before running.

        If there is no move file at that location in any of the loaded root directories, then a
        ValueError will be raised.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        if relative_path in self.__moves:
            return self.__moves[relative_path]

        for root_name, root in self.__roots.items():
            move_path = root / relative_path
            if move_path.exists():
                with open(move_path, "r", encoding="utf-8") as input_stream:
                    move = Move.from_tres(input_stream)
                    self.__moves[relative_path] = (root_name, move)

                    return (root_name, move)

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_moves(self, path: str) -> Dict[str, Tuple[RootName, Move]]:
        """
        Loads in all of the moves within the given res:// directory path.

        Looks for that path in all of the loaded root directories.

        Must have loaded at least one root before running.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        moves: Dict[str, Tuple[RootName, Move]] = {}
        for root_name, root in self.__roots.items():
            moves_dir_path = root / relative_path
            if moves_dir_path.exists():
                move_paths = sorted(moves_dir_path.glob("*.tres"))
                for move_path in move_paths:
                    move_relative_path = relative_path / move_path.name

                    if f"res://{move_relative_path}" in self.__moves_to_ignore:
                        continue

                    if move_relative_path in self.__moves:
                        moves[f"res://{move_relative_path}"] = self.__moves[
                            move_relative_path
                        ]
                        continue

                    with open(move_path, "r", encoding="utf-8") as input_stream:
                        move = Move.from_tres(input_stream)

                        moves[f"res://{move_relative_path}"] = (root_name, move)
                        self.__moves[move_relative_path] = (root_name, move)

        return moves

    def load_item(self, path: str) -> Tuple[RootName, Item]:
        """
        Loads in the item at the given res:// filepath.

        Must have loaded at least one root before running.

        If there is no item file at that location in any of the loaded root directories, then a
        ValueError will be raised.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        if relative_path in self.__moves:
            return self.__items[relative_path]

        for root_name, root in self.__roots.items():
            item_path = root / relative_path
            if item_path.exists():
                with open(item_path, "r", encoding="utf-8") as input_stream:
                    item = Item.from_tres(input_stream)
                    self.__items[relative_path] = (root_name, item)

                    return (root_name, item)

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_items(self, path: str) -> Dict[str, Tuple[RootName, Item]]:
        """
        Loads in all of the items within the given res:// directory path.

        Looks for that path in all of the loaded root directories.

        Must have loaded at least one root before running.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        items: Dict[str, Tuple[RootName, Item]] = {}
        for root_name, root in self.__roots.items():
            items_dir_path = root / relative_path
            if items_dir_path.exists():
                item_paths = sorted(items_dir_path.glob("*.tres"))
                for item_path in item_paths:
                    item_relative_path = relative_path / item_path.name

                    if item_relative_path in self.__moves:
                        items[f"res://{item_relative_path}"] = self.__items[
                            item_relative_path
                        ]
                        continue

                    with open(item_path, "r", encoding="utf-8") as input_stream:
                        item = Item.from_tres(input_stream)

                        items[f"res://{item_relative_path}"] = (root_name, item)
                        self.__items[item_relative_path] = (root_name, item)

        return items

    def lookup_filepath(self, path: str) -> pathlib.Path:
        """
        Returns a real filesystem path to the file at the given res:// path.

        If there is no file at that location in any of the loaded root directories, then a
        ValueError will be raised.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        for root in self.__roots.values():
            filepath = root / relative_path

            if filepath.exists():
                return filepath

        raise ValueError(f"Could not find file at path: {path}")

    def translate(self, string: str, locale: Optional[str] = None) -> str:
        """
        Translates the given string to the specified locale. Locale defaults to English (en).

        Must have loaded at least one root before running.

        If the string is not found for the given locale in any of the translation tables in any of
        the loaded root directories, then the given string will be returned.

        If no translation tables have been loaded for the given locale, then a ValueError will be
        raised.
        """
        self.__check_if_root_loaded()
        locale = locale if locale is not None else self.__default_locale

        if locale not in self.__translation_tables:
            raise ValueError(
                f"No translation tables for locale '{locale}' have been loaded. Only loaded locales are: {','.join(sorted(self.__translation_tables.keys()))}"
            )

        for table in self.__translation_tables[locale]:
            try:
                return table[string]
            except KeyError:
                pass

        return string

    def get_locales(self) -> Set[str]:
        """
        Returns a set of the locales (languages) that translation files have been loaded in for.
        """
        return set(self.__translation_tables.keys())

    def get_monster_forms_by_tags(
        self, tags: Iterable[str], include_any: bool = True
    ) -> Dict[str, Tuple[RootName, MonsterForm]]:
        """
        Returns all of the monster forms that have any of the given tags.
        """
        monster_forms = {}
        for tag in tags:
            for path, (root_name, monster_form) in self.__monster_forms.items():
                if tag in monster_form.move_tags or (include_any and tag == "any"):
                    monster_forms[f"res://{path}"] = (root_name, monster_form)

        return monster_forms

    def get_moves_by_tags(
        self, tags: Iterable[str]
    ) -> Dict[str, Tuple[RootName, Move]]:
        """
        Returns all of the moves that have any of the given tags.
        """
        moves = {}
        for tag in tags:
            for path, (root_name, move) in self.__moves.items():
                if tag in move.tags:
                    moves[f"res://{path}"] = (root_name, move)

        return moves

    def __check_if_root_loaded(self) -> None:
        if len(self.__roots) == 0:
            raise RuntimeError(
                "No roots have been loaded. You must load a root with `hoylake.load_root` before querying."
            )

    def __load_translation_tables(self, root: pathlib.Path) -> None:
        logging.debug(f"Looking for translation files in root: {root}")
        translation_filepaths = sorted(root.glob("**/*.translation"))
        logging.debug(
            f"Found {len(translation_filepaths)} translation files in: {root}"
        )
        for translation_filepath in translation_filepaths:
            logging.debug(f"Trying to load translation file: {translation_filepath}")
            with open(translation_filepath, "rb") as input_stream:
                table, locale = TranslationTable.from_translation(input_stream)
                self.__translation_tables[locale].append(table)
                logging.debug(
                    f"Successfully loaded {locale} translation file: {translation_filepath}"
                )
        logging.debug(
            f"Successfully loaded {len(translation_filepaths)} translation files of locales {','.join(sorted(self.__translation_tables.keys()))}."
        )

    @staticmethod
    def __parse_res_path(path: str) -> RelativeResPath:
        assert path.startswith("res://"), path

        return pathlib.Path(path.split("res://")[1])
