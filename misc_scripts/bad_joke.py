import pandas as pd

locales = [
    "en",
    "de_DE",
    "es_ES",
    "es_MX",
    "fr_FR",
    "it_IT",
    "ja_JP",
    "ko_KR",
    "pt_BR",
    "zh_CN",
]

with open("data/bad_jokes_by_language.txt", "w") as output_stream:
    data = pd.read_csv("data/bad_jokes.csv")
    for locale in locales:
        print("\n\n\n\n\n\n\n\n\n", file=output_stream)
        print(locale, file=output_stream)
        for value in data[locale]:
            print(f"<tr><td>{value}</td></tr>", file=output_stream)
