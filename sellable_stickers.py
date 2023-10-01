from typing import List

import argparse
import sys

SUCCESS = 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--battle_move_files", nargs="+", required=True)

    args = parser.parse_args(argv)

    results = {"sellable": [], "unsellable": []}
    for filepath in args.battle_move_files:
        with open(filepath, "r") as input_stream:
            for line in input_stream:
                if "unsellable" in line:
                    results["unsellable"].append(filepath)
                    break
            else:
                results["sellable"].append(filepath)

    print("filename,is_sellable")
    for sticker in sorted(results["sellable"]):
        print(f"{sticker},sellable")

    for sticker in sorted(results["unsellable"]):
        print(f"{sticker},unsellable")

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
