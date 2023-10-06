from typing import Dict, List

import collections
import logging
import pathlib

from .monster_form import MonsterForm
from .translation_table import TranslationTable

RelativeResPath = pathlib.Path


class Hoylake:
    def __init__(self) -> None:
        self.__roots: List[pathlib.Path] = []
        self.__translation_tables: collections.defaultdict[
            str, List[TranslationTable]
        ] = collections.defaultdict(lambda: [])

        self.__monster_forms: Dict[RelativeResPath, MonsterForm] = {}

    def load_root(self, new_root: pathlib.Path) -> None:
        logging.info(f"Loading new root directory: {new_root}")

        self.__roots.append(new_root)
        self.__load_translation_tables(new_root)

    def load_monster_form(self, path: str) -> MonsterForm:
        relative_path = Hoylake.__parse_res_path(path)

        if relative_path in self.__monster_forms:
            return self.__monster_forms[relative_path]

        for root in self.__roots:
            monster_path = root / relative_path
            if monster_path.exists():
                with open(monster_path, "r") as input_stream:
                    monster_form = MonsterForm.from_tres(input_stream)
                    self.__monster_forms[relative_path] = monster_form

                    return monster_form

        raise ValueError(f"Could not find monster file at path: {path}")

    def load_monster_forms(self, path: str) -> Dict[str, MonsterForm]:
        relative_path = Hoylake.__parse_res_path(path)

        monster_forms: Dict[str, MonsterForm] = {}
        for root in self.__roots:
            monsters_dir_path = root / relative_path
            if monsters_dir_path.exists():
                monster_paths = sorted(monsters_dir_path.glob("*.tres"))
                for monster_path in monster_paths:
                    with open(monster_path, "r") as input_stream:
                        monster_form = MonsterForm.from_tres(input_stream)
                        self.__monster_forms[relative_path] = monster_form

                        monster_relative_path = relative_path / monster_path.name
                        monster_forms[f"res://{monster_relative_path}"] = monster_form
                        self.__monster_forms[monster_relative_path] = monster_form

        return monster_forms

    def translate(self, string: str, locale: str = "en") -> str:
        if locale not in self.__translation_tables:
            raise ValueError(
                f"No translation tables for locale '{locale}' have been loaded. Only loaded locales are: {','.join(sorted(self.__translation_tables.keys()))}"
            )

        for table in self.__translation_tables[locale]:
            try:
                return table[string]
            except KeyError:
                pass

        raise KeyError(string)

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