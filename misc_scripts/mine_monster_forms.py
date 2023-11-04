from typing import Dict, List, Tuple

import argparse
import dataclasses
import json
import pathlib
import sys

import cbpickaxe as cbp

SUCCESS = 0
FAILURE = 1


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument("--monster_form_tres_files", nargs="+", required=True)

    args = parser.parse_args(argv)

    hoylake = cbp.Hoylake()
    for i, root in enumerate(args.roots):
        hoylake.load_root(str(i), pathlib.Path(root))

    monster_forms: List[Tuple[int, cbp.MonsterForm]] = []
    for input_file in args.monster_form_tres_files:
        with open(input_file, "r") as input_stream:
            monster_form = cbp.MonsterForm.from_tres(input_stream)

        monster_forms.append((monster_form.bestiary_index, monster_form))

    with open(pathlib.Path("data") / "monster_forms.json", "w") as output_stream:
        data = []
        for _, monster_form in sorted(monster_forms, key=lambda e: (e[0], e[1].name)):
            monster_form_dict = dataclasses.asdict(monster_form)
            monster_form_dict["name_en"] = hoylake.translate(monster_form.name)
            monster_form_dict["max_move_slots"] = monster_form.max_move_slots

            data.append(monster_form_dict)

        json.dump(data, output_stream, indent=4)

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
