Get move users
==============
This script can be used to generate a spreadsheet (`.csv`) of all of the monster species that can use the given moves.

You need to provide it paths to the decompiled copy of the game and decompiled or source code versions of any mods you want the script to take into account. If you want to load monster species from mods, you will also need to provide them like `--monster_form_paths res://data/monster_forms/ res://data/monster_forms_secret/ res://mods/data/monster_forms/`, where the last path points to the directory that contains the monster forms.

You also need to provide the path(s) to the directory of moves that you want the spreadsheet to include.

.. code-block:: bash

    cbpickaxe_get_move_users \
        --root "data/Cassette Beasts" data/synergy_is_fun_v1 \
        --move_paths res://mods/synergy_is_fun/battle_moves \

.. code-block:: bash

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