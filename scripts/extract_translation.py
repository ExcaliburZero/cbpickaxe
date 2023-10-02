from typing import List

import argparse
import csv
import json
import pathlib
import re
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("translation_files", nargs="+")

    args = parser.parse_args(argv)

    with open(pathlib.Path("data") / "monster_forms.json", "r") as input_stream:
        monster_forms = json.load(input_stream)
        strings_to_translate = [form["name"] for form in monster_forms]

    tables = {}
    for translation_filepath in args.translation_files:
        with open(translation_filepath, "rb") as input_stream:
            translation_table = cbp.TranslationTable.from_translation(
                input_stream, strings_to_translate
            )

        tables[translation_filepath] = translation_table

    locales = {
        translation_filepath: pathlib.Path(translation_filepath).name.split(".")[-2]
        for translation_filepath in args.translation_files
    }

    with open("translation_strings.csv", "w") as ouput_stream:
        writer = csv.DictWriter(
            ouput_stream, fieldnames=["id", *sorted(set(locales.values()))]
        )
        writer.writeheader()

        for i in strings_to_translate:
            row = {
                "id": i,
            }
            for name, table in tables.items():
                locale = locales[name]
                message = table.messages.get(i, "")
                assert isinstance(message, str)

                if message != "":
                    row[locale] = message

            writer.writerow(row)

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
