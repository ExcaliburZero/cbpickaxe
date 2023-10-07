# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from typing import List

import argparse
import csv
import pathlib
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument("--move_paths", nargs="+", required=True)
    parser.add_argument(
        "--monster_form_paths",
        nargs="+",
        default=["res://data/monster_forms/", "res://data/monster_forms_secret/"],
    )

    args = parser.parse_args(argv)

    hoylake = cbp.Hoylake()
    for i, root in enumerate(args.roots):
        hoylake.load_root(str(i), pathlib.Path(root))

    for monsters_path in args.monster_form_paths:
        _ = hoylake.load_monster_forms(monsters_path)

    writer = csv.DictWriter(sys.stdout, fieldnames=["move", "users"])
    writer.writeheader()
    for moves_path in args.move_paths:
        for _, move in hoylake.load_moves(moves_path).items():
            users = [
                hoylake.translate(monster_form.name)
                for _, (_, monster_form) in sorted(
                    hoylake.get_monster_forms_by_tags(move[1].tags).items(),
                    key=lambda d: (
                        d[1][1].bestiary_index,
                        hoylake.translate(d[1][1].name),
                    ),
                )
            ]
            writer.writerow(
                {
                    "move": hoylake.translate(move[1].name),
                    "users": ", ".join(users),
                }
            )

    return SUCCESS


def main_without_args() -> int:
    return main(sys.argv[1:])
