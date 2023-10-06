from typing import List

import collections
import logging
import pathlib

from .translation_table import TranslationTable


class Hoylake:
    def __init__(self) -> None:
        self.__roots: List[pathlib.Path] = []
        self.__translation_tables: collections.defaultdict[
            str, List[TranslationTable]
        ] = collections.defaultdict(lambda: [])

    def load_root(self, new_root: pathlib.Path) -> None:
        logging.info(f"Loading new root directory: {new_root}")

        self.__roots.append(new_root)
        self.__load_translation_tables(new_root)

    def __load_translation_tables(self, root: pathlib.Path) -> None:
        translation_dir = root / "translation"
        logging.info(f"Looking for translation directory: {translation_dir}")
        if not translation_dir.exists():
            logging.info(f"No translation directory in new root: {root}")
            return

        logging.info(f"Translation directory exists, loading translation files...")
        translation_filepaths = sorted(translation_dir.glob("*.translation"))
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
