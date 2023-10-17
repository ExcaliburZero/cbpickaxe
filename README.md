# cbpickaxe [![Python library](https://github.com/ExcaliburZero/cbpickaxe/actions/workflows/python-library.yml/badge.svg)](https://github.com/ExcaliburZero/cbpickaxe/actions/workflows/python-library.yml) [![Documentation Status](https://readthedocs.org/projects/cbpickaxe/badge/?version=latest)](https://cbpickaxe.readthedocs.io/en/latest/?badge=latest)
A Python library and set of scripts for data mining the game Cassette Beasts.

```python
import cbpickaxe as cbp

hoylake = cbp.Hoylake()
hoylake.load_root("cassette_beasts", "Cassette Beasts")

for monster_form in hoylake.load_monster_forms("res://data/monster_forms/").values():
    monster_name = hoylake.translate(monster_form.name)
    print(path, monster_name, monster_form)
```

## Installation
```bash
git clone https://github.com/ExcaliburZero/cbpickaxe.git
cd cbpickaxe
pip install -e .
```

## Scripts
### Generate mod documentation
This script can be used to generate HTML pages that document monsters, moves, items, etc. added by a mod.

For a tutorial and detailed information on how to use the script, see the following page:

https://cbpickaxe.readthedocs.io/en/latest/generate_docs/intro.html

### Extract translation strings
This script can be used to extract the different translations of in-game text.

You need to provide it the translation files to pull the translated text from (in `translations/` in the decompilation).

You also need to provide it a text file that lists all of the ids of the in-game text you want the translations of. This is needed, as the translation files do not actually store the text ids, only the translated text and a way to look them up by id via hashing.
```bash
cbpickaxe_extract_translation \
    --translation_files translation/*.translation \
    --strings_text_files strings.txt \
    --output_file translated_strings.csv
```

```bash
$ cat strings.txt
MAGIKRAB_NAME
SPRINGHEEL_NAME
HOPSKIN_NAME
$ cat translated_strings.csv
id,de_DE,en,eo,es_ES,es_MX,fr_FR,it_IT,ja_JP,ko_KR,pt_BR,zh_CN
MAGIKRAB_NAME,Magikrabbe,Magikrab,[!!! Máágííkŕááb !!!],Magikangrejo,Magikangrejo,Magicrabe,Magistaceo,マギカツギ,마법게,Magikaranguejo,魔术蟹
SPRINGHEEL_NAME,Sprungfeder,Springheel,[!!! Spŕííñgh̀ééééł !!!],Botajack,Botajack,Ressortalon,Saltatore,ピョンジャック,폴짝깨비,Saltamola,弹簧腿
HOPSKIN_NAME,Hoppskin,Hopskin,[!!! Hôôpškííñ !!!],Brincagarra,Brincagarras,Sautepeau,Balzospello,ホップスキン,홉스킨,Pulagarra,蝠普金斯
```

### Get move users
This script can be used to generate a spreadsheet (`.csv`) of all of the monster species that can use the given moves.

You need to provide it paths to the decompiled copy of the game and decompiled or source code versions of any mods you want the script to take into account. If you want to load monster species from mods, you will also need to provide them like `--monster_form_paths res://data/monster_forms/ res://data/monster_forms_secret/ res://mods/data/monster_forms/`, where the last path points to the directory that contains the monster forms.

You also need to provide the path(s) to the directory of moves that you want the spreadsheet to include.
```bash
cbpickaxe_get_move_users \
    --root "data/Cassette Beasts" data/synergy_is_fun_v1 \
    --move_paths res://mods/synergy_is_fun/battle_moves \
    > move_users.csv
```

```bash
$ head move_users.csv
move,users
[SIF] Chilling Gust,"Wingloom, Mothmanic, Diveal, Scubalrus, Faucetear, Fountess, Sparktan, Zeustrike, Shining Kuneko, Undyin, Spooki-onna, Diveberg"
[SIF] Controlled Burn,"Blossomaw, Gearyu, Busheye, Huntorch, Hedgeherne, Jumpkin, Beanstalker, Draculeaf, Rockertrice, Adeptile"
[SIF] Crop Raze,"Blossomaw, Gearyu, Busheye, Huntorch, Hedgeherne, Jumpkin, Beanstalker, Draculeaf, Rockertrice, Adeptile"
[SIF] Crop Rotation,"Sirenade, Decibelle, Dandylion, Blossomaw, Clocksley, Robindam, Muskrateer, Ratcousel, Elfless, Grampus, Faerious, Busheye, Huntorch, Hedgeherne, Jumpkin, Beanstalker, Draculeaf, Pawndead, Skelevangelist, Kingrave, Queenyx"
[SIF] Dandelion Puff,"Umbrahella, Dominoth, Wingloom, Mothmanic, Tokusect, Padpole, Frillypad, Liligator, Jellyton, Shining Kuneko, Khepri, Ferriclaw, Auriclaw"
[SIF] Fertile Soil,"Busheye, Huntorch, Hedgeherne, Jumpkin, Beanstalker, Draculeaf"
[SIF] Graze,"Littlered, Rosehood, Scarleteeth, Candevil, Malchemy, Miasmodeus, Vendemon, Gumbaal, Wooltergeist, Ramtasm, Zombleat, Capricorpse, Dandylion, Blossomaw, Macabra, Folklord, Dominoth, Wingloom, Mothmanic, Tokusect, Manispear, Palangolin, Kittelly, Cat-5, Puppercut, Southpaw, Ratcousel, Terracooka, Coaldron, Jumpkin, Beanstalker, Draculeaf, Anathema, Trapwurm, Wyrmaw"
[SIF] Greenhouse,"Lobstacle, Sanzatime, Fortiwinx, Burnace, Smogmagog, Pondwalker, Sharktanker, Averevoir"
[SIF] Growth Chemicals,"Aeroboros, Malchemy, Miasmodeus, Brushroom, Fungogh, Busheye, Huntorch, Hedgeherne, Jumpkin, Beanstalker, Draculeaf, Burnace, Smogmagog, Ferriclaw, Auriclaw"
```