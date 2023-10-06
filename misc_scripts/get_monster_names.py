from typing import List

import argparse
import json
import pathlib
import sys

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    with open(pathlib.Path("data") / "monster_forms.json", "r") as input_stream:
        monster_forms = json.load(input_stream)
        strings_to_translate = [form["name"] for form in monster_forms]

    with open(pathlib.Path("data") / "monster_names.txt", "w") as output_stream:
        for line in strings_to_translate:
            output_stream.write(f"{line}\n")

    return SUCCESS


def main_without_args() -> int:
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main_without_args())
