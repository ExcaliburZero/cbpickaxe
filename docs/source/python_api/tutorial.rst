Tutorial
========
To see how the library works, let's try running through a few basic usages.

Initial setup
-------------
Before proceding, you will need to make sure you have the following software installed:

* Python
* Git

Additionally you will already need to have `decompiled Cassette Beasts <https://wiki.cassettebeasts.com/wiki/Modding:Mod_Developer_Guide#Decompiling_Cassette_Beasts>`_.

Installing cbpickaxe
--------------------
In order to be able to use cbpickaxe, you will first need to install it.

First you will need to clone the GitHub repository that cbpickaxe is stored in. You can do that by running the following command in the temrinal:

.. code-block:: bash

   git clone https://github.com/ExcaliburZero/cbpickaxe.git

Next you can run the following commands in order to install cbpickaxe:

.. code-block:: bash

   cd cbpickaxe
   pip install -e .

Reading monster species information
-----------------------------------
First let's try getting some information on a monster species.

You will first need to create a `Hoylake` object and tell it where your decompiled copy of Cassette Beasts is.

.. code-block:: python

    import cbpickaxe as cbp

    hoylake = cbp.Hoylake()
    hoylake.load_root("cassette_beasts", "path_to/your_decompiled_copy_of/cassette_beasts")

Next we will need to figure out where the monster species information is located.

In the decompiled copy of Cassette Beasts, most of the monster species (also called monster forms) files are located in the `data/monster_forms` folder. We can refer to this location as `res://data/monster_forms`, where `res://` indicates a path that is relative to the main folder of the decompiled game copy.

As a start, we will get the information for Traffikrab, which is located at `res://data/monster_forms/traffikrab.tres`.

.. code-block:: python

    _, traffikrab = hoylake.load_monster_form("res://data/monster_forms/traffikrab.tres")
    print(traffikrab)

The output from the print statement will look like:

.. code-block::

    MonsterForm(name='TRAFFIKRAB_NAME', elemental_types=['plastic'], exp_yield=40, require_dlc='', pronouns=0, description='TRAFFIKRAB_DESCRIPTION', max_hp=80, melee_attack=120, melee_defense=80, ranged_attack=120, ranged_defense=110, speed=90, accuracy=100, evasion=100, max_ap=5, move_slots=4, evolutions=[Evolution(name='magikrab', evolved_form='res://data/monster_forms_secret/magikrab.tres'), Evolution(name='lobstacle', evolved_form='res://data/monster_forms/lobstacle.tres'), Evolution(name='weevilite', evolved_form='res://data/monster_forms/weevilite.tres')], bestiary_index=11, move_tags=['traffikrab', 'crab', 'traffic', 'rage', 'junk', 'deception'], battle_sprite_path='res://sprites/monsters/traffikrab.json', tape_upgrades=[TapeUpgrade(name='Slot + elemental_wall', add_slot=True), TapeUpgrade(name='Slot + inflame', add_slot=True), 'res://data/battle_moves/multi_smack.tres', TapeUpgrade(name='coating_water', add_slot=False), 'res://data/battle_moves/undertow.tres'], bestiary_bios=['TRAFFIKRAB_LORE_1', 'TRAFFIKRAB_LORE_2'])

We can also look at just specific information about the monster species by accessing specific attributes:

.. code-block:: python

    print(traffikrab.name)
    print(traffikrab.elemental_types)
    print(traffikrab.max_hp)
    print(traffikrab.bestiary_bios)

.. code-block::

    TRAFFIKRAB_NAME
    ['plastic']
    80
    ['TRAFFIKRAB_LORE_1', 'TRAFFIKRAB_LORE_2']

String IDs and translation
--------------------------
You'll notice that for the name and bestiary entries above they are in all capital letters. This indicates that they are not the actual values but are string ids. In order to see the actual values we will need to have them translated into a specific locale (language & region).

You can ask Hoylake to translate them:

.. code-block:: python

    print(hoylake.translate(traffikrab.name))
    print(hoylake.translate(traffikrab.bestiary_bios[0]))
    print(hoylake.translate(traffikrab.bestiary_bios[1]))

.. code-block::

    Traffikrab
    The Traffikrab’s cone isn’t actually part of its body – it is merely a traffic cone that has washed up on the shores of New Wirral and been occupied by the creature. It is said that in the past, they would instead find other objects to live inside.
    The traffic cone was invented by Charles D. Scanlon in the 1940’s as a low-maintenance way to signal road repairs. Commonly made of orange or yellow plastic, they can also feature a white reflective stripe to increase visibility at night.

The reason for this is because when playing the game in other languages, using string ids makes it easier for the game to use the corresponding names/text for the player's language.

For example, you can also ask Hoylake to translate them into another locale, in this we'll ask him to translate them into Spanish (Latin America).

.. code-block:: python

    print(hoylake.translate(traffikrab.name, locale="es_MX"))
    print(hoylake.translate(traffikrab.bestiary_bios[0], locale="es_MX"))
    print(hoylake.translate(traffikrab.bestiary_bios[1], locale="es_MX"))

.. code-block::

    Trafikangrejo
    El cono del trafikangrejo no es parte de su cuerpo, sino un simple cono de carretera que la marea arrastró a la costa de Nueva Wirral y que este ser decidió habitar. Se dice que en el pasado buscaban objetos distintos en los que vivir.
    El cono de carretera lo inventó Charles D. Scanlon en la década de 1940 como una forma sencilla y barata de señalizar las obras en la carretera. A menudo se fabrican con plástico naranja o amarillo, y puede añadírseles una franja reflectante blanca para aumentar su visibilidad por la noche.