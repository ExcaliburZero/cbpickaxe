from typing import Dict, List

import argparse
import pathlib
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument(
        "--monster_form_paths",
        nargs="+",
        default=["res://data/monster_forms/", "res://data/monster_forms_secret/"],
    )

    args = parser.parse_args(argv)

    hoylake = cbp.Hoylake()
    for root in args.roots:
        hoylake.load_root(pathlib.Path(root))

    monster_forms = {}
    for monster_forms_path in args.monster_form_paths:
        monster_forms.update(hoylake.load_monster_forms(monster_forms_path))

    print("{{#switch: {{{1|}}}")
    for _, monster_form in sorted(
        monster_forms.items(),
        key=lambda d: (d[1].bestiary_index, hoylake.translate(d[1].name)),
    ):
        print(
            f"| {hoylake.translate(monster_form.name)} = {monster_form.max_move_slots}"
        )
    print("| #default = Unknown")
    print("}}")

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
