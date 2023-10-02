from typing import List

import argparse
import sys
import time

from mss import mss

import pyautogui

SUCCESS = 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("--type", required=True)

    args = parser.parse_args(argv)

    time.sleep(5)

    for i in range(0, 139):
        print(i)
        with mss() as sct:
            filepath = f"{args.type}_{i}.png"
            sct.shot(mon=2, output=filepath)
        pyautogui.press("down")
        time.sleep(0.5)

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
