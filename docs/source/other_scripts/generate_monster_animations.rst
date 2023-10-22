Generate monster animations
===========================
This script can be used to generate animated gifs of monster battle animations.

You need to provide it the path to your decompiled copy of *Cassette Beasts* and/or the mods you want to generate animations from.

.. code-block:: bash

    cbpickaxe_generate_monster_animations \
        --roots my_decompiled_copy_of_cassette_beasts \
        --output_directory monster_animations \
        --crop

Flags
-----

.. table::

    +------------------------+-----------+---------------------------------------+-----------------------------------------------------------------------------+
    | Name                   | Type      | Default                               | Description                                                                 |
    +========================+===========+=======================================+=============================================================================+
    | `--roots`              | List[str] |                                       | Roots to look for data files in (ex. decompiled copy of *Cassette Beasts*). |
    +------------------------+-----------+---------------------------------------+-----------------------------------------------------------------------------+
    | `--output_directory`   | str       |                                       | Directory to store the monster animation files in.                          |
    +------------------------+-----------+---------------------------------------+-----------------------------------------------------------------------------+
    | `--crop`               |           | False                                 | If provided, will crop the monster animations to only the area taken up by  |
    |                        |           |                                       | that animation.                                                             |
    +------------------------+-----------+---------------------------------------+-----------------------------------------------------------------------------+
    | `--monster_form_paths` | List[str] | res://data/monster_forms/ |br|        | Resource filepaths to look for monster forms in.                            |
    |                        |           | res://data/monster_forms_secret/ |br| |                                                                             |
    |                        |           | res://data/monster_forms_unlisted/    | |br|                                                                        |
    |                        |           |                                       |                                                                             |
    |                        |           |                                       | Each can be either a path to a folder containing monster form `.tres` files |
    |                        |           |                                       | or paths to individual `.tres` monster form files.                          |
    +------------------------+-----------+---------------------------------------+-----------------------------------------------------------------------------+