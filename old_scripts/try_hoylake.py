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
    for root in args.roots:
        hoylake.load_root(pathlib.Path(root))

    traffikrab = hoylake.load_monster_form("res://data/monster_forms/traffikrab.tres")
    print(traffikrab)
    print(hoylake.translate(traffikrab.name))
    print(hoylake.translate(traffikrab.description))
    for form in traffikrab.evolutions:
        evo = hoylake.load_monster_form(form.evolved_form)
        print(evo)

    traffikrabdos = hoylake.load_monster_form(
        "res://mods/de_example_monster/traffikrabdos.tres"
    )
    print(traffikrabdos)
    print(hoylake.translate(traffikrabdos.description))

    return SUCCESS


if __name__ == "__main__":
    main(sys.argv[1:])
