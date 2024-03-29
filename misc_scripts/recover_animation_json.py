# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
from typing import List

import argparse
import pathlib
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--compiled_animation_files", nargs="+", required=True)
    parser.add_argument("--output_directory", required=True)

    args = parser.parse_args(argv)

    for filepath in args.compiled_animation_files:
        filepath = pathlib.Path(filepath)

        with open(filepath, "rb") as input_stream:
            try:
                animation = cbp.Animation.from_scn(input_stream)
            except Exception as e:
                raise ValueError(
                    f"Failed to load/convert animation compiled json: {filepath}"
                ) from e
            for a in animation:
                print(a)

    return SUCCESS


def main_without_args() -> int:
    return main(sys.argv[1:])
