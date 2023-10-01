from typing import Dict, List

import argparse
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("monster_form_tres_files", nargs="+")

    args = parser.parse_args(argv)

    monster_forms: Dict[int, cbp.MonsterForm] = {}
    for input_file in args.monster_form_tres_files:
        with open(input_file, "r") as input_stream:
            monster_form = cbp.MonsterForm.from_tres(input_stream)

        monster_forms[monster_form.bestiary_index] = monster_form

    for _, monster_form in sorted(monster_forms.items()):
        print(monster_form)

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
