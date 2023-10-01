# cbpickaxe
A Python library and set of scripts for data mining the game Cassette Beasts.

```python
import cbpickaxe as cbp

with open("trafikrab.tres", "r") as input_stream:
    monster = cbp.MonsterForm.from_tres(input_stream)

print(monster)
print(monster.bestiary_index)
print(monster.move_slots)
```

## Installation
```bash
git clone https://github.com/ExcaliburZero/cbpickaxe.git
cd cbbpickaxe
pip install -e .
```