from typing import Dict, List

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
    parser.add_argument("--names_files", nargs="+", required=True)
    parser.add_argument("--output_file", required=True)
    parser.add_argument("--ignore_locales", nargs="*", default=["eo"])

    args = parser.parse_args(argv)

    hoylake = cbp.Hoylake()
    for i, root in enumerate(args.roots):
        hoylake.load_root(str(i), pathlib.Path(root))

    locales = hoylake.get_locales()
    for locale_to_ignore in args.ignore_locales:
        locales.remove(locale_to_ignore)

    translated_names: Dict[str, Dict[str, str]] = {}
    for name_filepath in args.names_files:
        with open(name_filepath, "r", encoding="utf-8") as input_stream:
            for string in input_stream:
                string = string.strip()

                translated_names[string] = {
                    locale: hoylake.translate(string, locale=locale)
                    for locale in locales
                }

    with open(args.output_file, "w", encoding="utf-8") as output_stream:
        for string, translations in translated_names.items():
            output_stream.write(f"{translations['en']}\n")
            output_stream.write("{{NameTranslations\n")
            for locale in sorted(locales):
                if locale == "en":
                    continue

                output_stream.write(f"| {locale} = {translations[locale]}\n")

            output_stream.write("}}\n")

    return SUCCESS


if __name__ == "__main__":
    main(sys.argv[1:])
