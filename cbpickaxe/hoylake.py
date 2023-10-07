"""
Code for loading in data files and querying data from them.
"""
from typing import Dict, List, Iterable, Set

import collections
import json
import logging
import pathlib

from .animation import Animation
from .monster_form import MonsterForm
from .move import Move
from .translation_table import TranslationTable

RelativeResPath = pathlib.Path


class Hoylake:
    """
    A class that handles loading in data files from the decompiled game.
    """

    def __init__(self) -> None:
        self.__roots: List[pathlib.Path] = []
        self.__translation_tables: collections.defaultdict[
            str, List[TranslationTable]
        ] = collections.defaultdict(lambda: [])

        self.__monster_forms: Dict[RelativeResPath, MonsterForm] = {}
        self.__moves: Dict[RelativeResPath, Move] = {}
        self.__animations: Dict[RelativeResPath, Animation] = {}

        self.__moves_to_ignore = ["res://data/battle_moves/placeholder.tres"]

    def load_root(self, new_root: pathlib.Path) -> None:
        """
        Adds the given root directory to the list of known root directories.

        Can be called multiple times in order to load multiple root directories
        (ex. base game, DLC, mods).

        Must be run at least once before loading in any files (ex. monster forms).
        """
        logging.info(f"Loading new root directory: {new_root}")

        self.__roots.append(new_root)
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
            return self.__animations[relative_path]

        for root in self.__roots:
            animation_path = root / relative_path
            if animation_path.exists():
                with open(animation_path, "r", encoding="utf-8") as input_stream:
                    animation = Animation.from_dict(json.load(input_stream))
                    self.__animations[relative_path] = animation

                    return animation

        raise ValueError(f"Could not find animation file at path: {path}")

    def load_monster_form(self, path: str) -> MonsterForm:
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

        for root in self.__roots:
            monster_path = root / relative_path
            if monster_path.exists():
                with open(monster_path, "r", encoding="utf-8") as input_stream:
                    monster_form = MonsterForm.from_tres(input_stream)
                    self.__monster_forms[relative_path] = monster_form

                    return monster_form

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_monster_forms(self, path: str) -> Dict[str, MonsterForm]:
        """
        Loads in all of the monster forms within the given res:// directory path.

        Looks for that path in all of the loaded root directories.

        Must have loaded at least one root before running.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        monster_forms: Dict[str, MonsterForm] = {}
        for root in self.__roots:
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
                        monster_forms[f"res://{monster_relative_path}"] = monster_form
                        self.__monster_forms[monster_relative_path] = monster_form

        return monster_forms

    def load_move(self, path: str) -> Move:
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

        for root in self.__roots:
            move_path = root / relative_path
            if move_path.exists():
                with open(move_path, "r", encoding="utf-8") as input_stream:
                    move = Move.from_tres(input_stream)
                    self.__moves[relative_path] = move

                    return move

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_moves(self, path: str) -> Dict[str, Move]:
        """
        Loads in all of the moves within the given res:// directory path.

        Looks for that path in all of the loaded root directories.

        Must have loaded at least one root before running.
        """
        self.__check_if_root_loaded()

        relative_path = Hoylake.__parse_res_path(path)

        moves: Dict[str, Move] = {}
        for root in self.__roots:
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

                        moves[f"res://{move_relative_path}"] = move
                        self.__moves[move_relative_path] = move

        return moves

    def translate(self, string: str, locale: str = "en") -> str:
        """
        Translates the given string to the specified locale. Locale defaults to English (en).

        Must have loaded at least one root before running.

        If the string is not found for the given locale in any of the translation tables in any of
        the loaded root directories, then the given string will be returned.

        If no translation tables have been loaded for the given locale, then a ValueError will be
        raised.
        """
        self.__check_if_root_loaded()

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

    def get_monster_forms_by_tags(self, tags: Iterable[str]) -> Dict[str, MonsterForm]:
        """
        Returns all of the monster forms that have any of the given tags.
        """
        monster_forms = {}
        for tag in tags:
            for path, monster_form in self.__monster_forms.items():
                if tag in monster_form.move_tags:
                    monster_forms[f"res://{path}"] = monster_form

        return monster_forms

    def get_moves_by_tags(self, tags: Iterable[str]) -> Dict[str, Move]:
        """
        Returns all of the moves that have any of the given tags.
        """
        moves = {}
        for tag in tags:
            for path, move in self.__moves.items():
                if tag in move.tags:
                    moves[f"res://{path}"] = move

        return moves

    def __check_if_root_loaded(self) -> None:
        if len(self.__roots) == 0:
            raise RuntimeError(
                "No roots have been loaded. You must load a root with `hoylake.load_root` before querying."
            )

    def __load_translation_tables(self, root: pathlib.Path) -> None:
        logging.info(f"Looking for translation files in root: {root}")
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
        logging.info(
            f"Successfully loaded {len(translation_filepaths)} translation files of locales {','.join(sorted(self.__translation_tables.keys()))}."
        )

    @staticmethod
    def __parse_res_path(path: str) -> RelativeResPath:
        assert path.startswith("res://"), path

        return pathlib.Path(path.split("res://")[1])
