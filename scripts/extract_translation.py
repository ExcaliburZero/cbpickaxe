from typing import List

import argparse
import csv
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("translation_files", nargs="+")

    args = parser.parse_args(argv)

    tables = {}
    for translation_filepath in args.translation_files:
        with open(translation_filepath, "rb") as input_stream:
            translation_table = cbp.TranslationTable.from_translation(input_stream)

        tables[translation_filepath] = translation_table

    with open("translation_strings.csv", "w") as ouput_stream:
        writer = csv.DictWriter(
            ouput_stream, fieldnames=["id", *args.translation_files]
        )
        writer.writeheader()
        for i in sorted(list(tables.values())[0].messages.keys()):
            writer.writerow(
                {"id": i, **{name: table.messages[i] for name, table in tables.items()}}
            )

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
