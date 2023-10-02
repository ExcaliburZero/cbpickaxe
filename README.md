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
cd cbpickaxe
pip install -e .
```

## Scripts
### Extract translation strings
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