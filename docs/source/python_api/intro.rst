Python API
==========
**cbpickaxe** offers a Python API for reading in and working with data files from Cassette Beasts.

.. code-block:: python

    import cbpickaxe as cbp

    hoylake = cbp.Hoylake()
    hoylake.load_root("cassette_beasts", "Cassette Beasts")

    for monster_form in hoylake.load_monster_forms("res://data/monster_forms/").values():
        monster_name = hoylake.translate(monster_form.name)
        print(path, monster_name, monster_form)

.. toctree::
   :maxdepth: 2

   tutorial
   classes_and_methods