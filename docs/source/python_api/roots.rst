Roots
=====
**Roots** are filepaths where cbpickaxe will look for data files that have a resource path (`res://`).

When working with cbpickaxe you will typically need to load in your decompiled copy of *Cassette Beasts*, so that cbpickaxe will know where to look for data files. Additionally if you are working with mods, you will need to load each of them as roots as well.

When loading a root you will also need to give it a name. When you load data, you will typically also get the name of the root it was loaded from in case you want to know whether the data is from the base game or is from a mod.

.. code-block:: python

    import cbpickaxe as cbp

    hoylake = cbp.Hoylake()

    # Load decompiled copy of game
    hoylake.load_root("cassette_beasts", "Cassette Beasts")

    # Load mods
    hoylake.load_root("traffikrabdos", "traffikrabdos")
    hoylake.load_root("synergy_is_fun", "synergy_is_fun_v1")

How roots work
--------------
When you call `load_monster_form` or a similar method on a `Hoylake` object, you have to provide the resource path for that data (ex. `res://data/monster_forms/traffikrab.tres`).

.. code-block:: python

    hoylake.load_monster_form("res://data/monster_forms/traffikrab.tres")

Resource paths
^^^^^^^^^^^^^^
Resource paths consist of two parts:

* Prefix - Typically `res://`.
* Path - The location of the resource file relative to the "project root". For the example path above, the relative path would be `data/monster_forms/traffikrab.tres`.

For more information on how paths work for Godot projects (like *Cassette Beasts*), see `File paths in Godot projects <https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html>`_.

Resource loading
^^^^^^^^^^^^^^^^
When calling a method like `load_monster_form`, the `Hoylake` object will look though each of the loaded roots to try and find the requested data file(s).

For example, if you have three loaded roots (`"Cassette Beasts"`, `"traffikrabdos"`, and `"synergy_is_fun_v1"`) and you try to load `res://data/monster_forms/traffikrab.tres`, then the following will happen.

#. It will look in `"Cassette Beasts"` to see if `Cassette Beasts/data/monster_forms/traffikrab.tres` exists.
#. Since that file exists, it will parse that file and return the monster form data.

If you instead try to load `res://mods/de_example_monster/traffikrabdos.tres`, then the following will happen.

#. It will look in `"Cassette Beasts"` to see if `Cassette Beasts/mods/de_example_monster/traffikrabdos.tres` exists.
#. It will look in `"traffikrabdos"` to see if `traffikrabdos/mods/de_example_monster/traffikrabdos.tres` exists.
#. Since that file exists, it will parse that file and return the monster form data.