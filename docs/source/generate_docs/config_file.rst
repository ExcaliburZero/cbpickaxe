Configuration file
==================
**cbpickaxe_generate_docs** needs a configuration file in order to know what types of documentation to generate. By default, this is a file called `docs.toml`.

A new configuration file can be generated by running the following command:

.. code-block:: bash

   cbpickaxe_generate_docs new

Sections
--------
The configuration file is broken up into several sections:

* roots - Locations where the tool can find data files.
* moster_forms - Data about monster species.
* moves - Data about moves.
* items - Data about items.

Roots
-----
Roots are named filepaths where the tool will look for data files.

It is common to provide two roots, one for the decompiled copy of Cassette Beasts and one for your mod.

A root for Cassette Beasts must be provided, however, any number of additional roots can be provided (allowing generating documentation for multiple mods at once).

.. code-block:: toml

    [roots]
    cassette_beasts = "../Cassette_Beasts"
    traffikrabdos = "."

Monster Forms
-------------

.. code-block:: toml

    [monster_forms]
    paths = [
        "res://mods/de_example_monster/traffikrabdos.tres",
    ]
    include_official = false

.. table::

    +------------------+-----------------+----------------------------------------------------------------------------+
    | Name             | Type            | Description                                                                |
    +==================+=================+============================================================================+
    | paths            | List[str]       | Paths to `.tres` monster form files or directories that contain `.tres`    |
    |                  |                 | monster form files.                                                        |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to an empty list.                                                 |
    +------------------+-----------------+----------------------------------------------------------------------------+
    | include_official | bool            | Generates documentation for the monsters in the official game, in addition |
    |                  |                 | to the monsters added by mods.                                             |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to `false`.                                                       |
    +------------------+-----------------+----------------------------------------------------------------------------+

Moves
-----

.. code-block:: toml

    [moves]
    paths = [
        "res://mods/synergy_is_fun/battle_moves/"
    ]
    include_official = false

.. table::

    +------------------+-----------------+----------------------------------------------------------------------------+
    | Name             | Type            | Description                                                                |
    +==================+=================+============================================================================+
    | paths            | List[str]       | Paths to `.tres` move files or directories that contain `.tres` move       |
    |                  |                 | files.                                                                     |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to an empty list.                                                 |
    +------------------+-----------------+----------------------------------------------------------------------------+
    | include_official | bool            | Generates documentation for the moves in the official game, in addition to |
    |                  |                 | the moves added by mods.                                                   |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to `false`.                                                       |
    +------------------+-----------------+----------------------------------------------------------------------------+

Items
-----

.. code-block:: toml

    [items]
    paths = [
        "res://mods/gramophone_music_mod/MusicPlayerItem.tres",
    ]
    include_official = false

.. table::

    +------------------+-----------------+----------------------------------------------------------------------------+
    | Name             | Type            | Description                                                                |
    +==================+=================+============================================================================+
    | paths            | List[str]       | Paths to `.tres` item files or directories that contain `.tres` item       |
    |                  |                 | files.                                                                     |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to an empty list.                                                 |
    +------------------+-----------------+----------------------------------------------------------------------------+
    | include_official | bool            | Generates documentation for the items in the official game, in addition to |
    |                  |                 | the items added by mods.                                                   |
    |                  |                 |                                                                            |
    |                  |                 | |br|                                                                       |
    |                  |                 |                                                                            |
    |                  |                 | Defaults to `false`.                                                       |
    +------------------+-----------------+----------------------------------------------------------------------------+

Miscellaneous
-------------

.. code-block:: toml

    output_directory = "docs"

.. table::

    +------------------+-----------------+----------------------------------------------------------------------------+
    | Name             | Type            | Description                                                                |
    +==================+=================+============================================================================+
    | output_directory | string          | The filepath where generated documentation will be written to.             |
    +------------------+-----------------+----------------------------------------------------------------------------+