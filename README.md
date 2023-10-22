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
| Script        | Description |
| ------------- | ----------- |
| [generate_docs](https://cbpickaxe.readthedocs.io/en/latest/generate_docs/intro.html) | Generates HTML pages that document monsters, moves, items, etc. added by a mod. |
| [extract_translation](https://cbpickaxe.readthedocs.io/en/latest/other_scripts/extract_translation_strings.html) | Extracts the translations of given in-game text |
| [get_move_users](https://cbpickaxe.readthedocs.io/en/latest/other_scripts/get_move_users.html) | Finds all of the monster species that can use given moves. |
| [generate_monster_animations](https://cbpickaxe.readthedocs.io/en/latest/other_scripts/generate_monster_animations.html) | Creates animated gifs of monster battle animations. |