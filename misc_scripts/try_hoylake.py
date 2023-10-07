from typing import List

import argparse
import logging
import pathlib
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)

    args = parser.parse_args(argv)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    hoylake = cbp.Hoylake()
    for i, root in enumerate(args.roots):
        hoylake.load_root(str(i), pathlib.Path(root))

    _ = hoylake.load_monster_forms("res://data/monster_forms/")
    _ = hoylake.load_monster_forms("res://data/monster_forms_secret/")

    move = hoylake.load_move("res://data/battle_moves/carnivore.tres")[1]
    for path, monster_form in hoylake.get_monster_forms_by_tags(move.tags).items():
        print(path, monster_form)

    print("==========================")
    print("==========================")
    print("==========================")

    _ = hoylake.load_moves("res://data/battle_moves/")

    monster_form = hoylake.load_monster_form(
        "res://data/monster_forms/shining_kuneko.tres"
    )[1]
    for path, move in hoylake.get_moves_by_tags(monster_form.move_tags).items():
        print(path, move)

    print(len(hoylake.get_moves_by_tags(monster_form.move_tags + ["any"])))

    return SUCCESS


if __name__ == "__main__":
    main(sys.argv[1:])
