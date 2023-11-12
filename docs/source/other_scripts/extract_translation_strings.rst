Extract translation strings
===========================
This script can be used to extract the different translations of in-game text.

You need to provide it the translation files to pull the translated text from (in `translations/` in the decompilation).

You also need to provide it a text file that lists all of the ids of the in-game text you want the translations of. This is needed, as the translation files do not actually store the text ids, only the translated text and a way to look them up by id via hashing.

.. code-block:: bash

    cbpickaxe_extract_translation \
        --translation_files translation/*.translation \
        --strings_text_files strings.txt \
        --output_file translated_strings.csv

.. code-block:: bash

    $ cat strings.txt
    MAGIKRAB_NAME
    SPRINGHEEL_NAME
    HOPSKIN_NAME
    $ cat translated_strings.csv
    id,de_DE,en,eo,es_ES,es_MX,fr_FR,it_IT,ja_JP,ko_KR,pt_BR,zh_CN
    MAGIKRAB_NAME,Magikrabbe,Magikrab,[!!! Máágííkŕááb !!!],Magikangrejo,Magikangrejo,Magicrabe,Magistaceo,マギカツギ,마법게,Magikaranguejo,魔术蟹
    SPRINGHEEL_NAME,Sprungfeder,Springheel,[!!! Spŕííñgh̀ééééł !!!],Botajack,Botajack,Ressortalon,Saltatore,ピョンジャック,폴짝깨비,Saltamola,弹簧腿
    HOPSKIN_NAME,Hoppskin,Hopskin,[!!! Hôôpškííñ !!!],Brincagarra,Brincagarras,Sautepeau,Balzospello,ホップスキン,홉스킨,Pulagarra,蝠普金斯

Gender-specific strings
-----------------------
Some in-game strings are able to have different variants based on the player character's pronouns. For example, `AA_CUBE_POST_BATTLE_MEREDITH3` has three variants:

* `AA_CUBE_POST_BATTLE_MEREDITH3.f` (if player has she/her pronouns)
* `AA_CUBE_POST_BATTLE_MEREDITH3.m` (if player has he/him pronouns)
* `AA_CUBE_POST_BATTLE_MEREDITH3.n` (if player has they/them pronouns)

This script is able to automatically detect strings that have gender-variants, and will include all three versions of the string in the output csv.

.. code-block:: bash

    $ cat strings.txt
    AA_CUBE_POST_BATTLE_MEREDITH3
    $ cat translated_strings.csv
    id, ...
    AA_CUBE_POST_BATTLE_MEREDITH3.f, ...
    AA_CUBE_POST_BATTLE_MEREDITH3.m, ...
    AA_CUBE_POST_BATTLE_MEREDITH3.n, ...
