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

    for path, move in hoylake.load_moves("res://data/battle_moves/").items():
        print(path, move)

    return SUCCESS


if __name__ == "__main__":
    main(sys.argv[1:])
