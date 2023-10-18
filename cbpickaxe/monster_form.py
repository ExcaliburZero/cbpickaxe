"""
Classes related to monster forms (species).
"""
from dataclasses import dataclass
from typing import cast, IO, List, Optional, Union

import godot_parser as gp


@dataclass
class TapeUpgrade:
    """
    An activity that occurs when a monster tape reaches a specific grade level.
    """

    name: str
    add_slot: bool

    @staticmethod
    def from_sub_resource(sub_resource: gp.GDSubResourceSection) -> "TapeUpgrade":
        """
        Parses the given sub resource into a TapeUpgrade.
        """
        name = sub_resource["resource_name"]
        add_slot = sub_resource.get("add_slot", default=False)

        assert isinstance(name, str)
        assert isinstance(add_slot, bool)

        return TapeUpgrade(name=name, add_slot=add_slot)


@dataclass
class Evolution:
    """
    A remastering that a monster tape can undergo.
    """

    name: str
    evolved_form: str


@dataclass
class MonsterForm:
    """
    A monster form (species).
    """

    name: str
    swap_colors: List[gp.Color]
    default_palette: List[gp.Color]
    emission_palette: List[gp.Color]
    elemental_types: List[str]
    exp_yield: int
    require_dlc: str
    pronouns: int
    description: str
    max_hp: int
    melee_attack: int
    melee_defense: int
    ranged_attack: int
    ranged_defense: int
    speed: int
    accuracy: int
    evasion: int
    max_ap: int
    move_slots: int
    evolutions: List[Evolution]
    bestiary_index: int
    move_tags: List[str]
    battle_sprite_path: str
    tape_upgrades: List[Union[TapeUpgrade, str]]
    bestiary_bios: List[str]

    @property
    def max_move_slots(self) -> int:
        """
        The maximum number of move slots monsters of this form can have (ex. when at grade 5).
        """
        move_slot_increases = 0
        for upgrade in self.tape_upgrades:
            if isinstance(upgrade, str):
                pass
            else:
                assert isinstance(upgrade, TapeUpgrade)
                if upgrade.add_slot:
                    move_slot_increases += 1

        return self.move_slots + move_slot_increases

    @staticmethod
    def from_tres(input_stream: IO[str]) -> "MonsterForm":
        """
        Parses a MonsterForm from the given Godot ".tres" input stream.
        """
        scene = gp.parse(input_stream.read())

        name = None
        swap_colors = None
        default_palette = None
        emission_palette = None
        exp_yield = None
        require_dlc = None
        move_slots = None
        pronouns = None
        description = None
        max_hp = None
        melee_attack = None
        melee_defense = None
        ranged_attack = None
        ranged_defense = None
        speed = None
        accuracy = None
        evasion = None
        max_ap = None
        evolutions = None
        move_tags = None
        battle_sprite_path = None
        tape_upgrades: Optional[List[Union[TapeUpgrade, str]]] = None
        bestiary_bios = None

        for section in scene.get_sections():
            # pylint: disable-next=unidiomatic-typecheck
            if type(section) == gp.GDResourceSection:
                name = section["name"]
                swap_colors = section["swap_colors"]
                default_palette = section["default_palette"]
                emission_palette = section["emission_palette"]
                bestiary_index = section["bestiary_index"]
                move_slots = section["move_slots"]
                exp_yield = section["exp_yield"]
                require_dlc = section["require_dlc"]
                pronouns = section["pronouns"]
                description = section["description"]
                max_hp = section["max_hp"]
                melee_attack = section["melee_attack"]
                melee_defense = section["melee_defense"]
                ranged_attack = section["ranged_attack"]
                ranged_defense = section["ranged_defense"]
                speed = section["speed"]
                accuracy = section["accuracy"]
                evasion = section["evasion"]
                max_ap = section["max_ap"]
                move_tags = section["move_tags"]
                battle_sprite_path = section["battle_sprite_path"]
                bestiary_bios = section["bestiary_bios"]

                tape_upgrades = MonsterForm.__parse_tape_upgrades(scene, section)
                elemental_types = MonsterForm.__parse_elemental_types(scene, section)
                evolutions = MonsterForm.__parse_evolutions(scene, section)

        assert isinstance(name, str)
        assert isinstance(swap_colors, list)
        assert isinstance(default_palette, list)
        assert isinstance(emission_palette, list)
        assert isinstance(bestiary_index, int)
        assert isinstance(move_slots, int)
        assert isinstance(exp_yield, int)
        assert isinstance(require_dlc, str)
        assert isinstance(pronouns, int)
        assert isinstance(description, str)
        assert isinstance(max_hp, int)
        assert isinstance(melee_attack, int)
        assert isinstance(melee_defense, int)
        assert isinstance(ranged_attack, int)
        assert isinstance(ranged_defense, int)
        assert isinstance(speed, int)
        assert isinstance(accuracy, int)
        assert isinstance(evasion, int)
        assert isinstance(max_ap, int)
        assert isinstance(battle_sprite_path, str)
        assert isinstance(move_tags, list)
        assert isinstance(bestiary_bios, list)
        assert tape_upgrades is not None
        assert evolutions is not None

        for color in emission_palette:
            assert isinstance(color, gp.Color)
        emission_palette = cast(List[gp.Color], emission_palette)

        for color in swap_colors:
            assert isinstance(color, gp.Color)
        swap_colors = cast(List[gp.Color], swap_colors)

        for color in default_palette:
            assert isinstance(color, gp.Color)
        default_palette = cast(List[gp.Color], default_palette)

        for tag in move_tags:
            assert isinstance(tag, str)
        move_tags = cast(List[str], move_tags)

        for bio in bestiary_bios:
            assert isinstance(bio, str)
        bestiary_bios = cast(List[str], bestiary_bios)

        return MonsterForm(
            name=name,
            swap_colors=swap_colors,
            default_palette=default_palette,
            emission_palette=emission_palette,
            elemental_types=elemental_types,
            exp_yield=exp_yield,
            require_dlc=require_dlc,
            pronouns=pronouns,
            description=description,
            max_hp=max_hp,
            melee_attack=melee_attack,
            melee_defense=melee_defense,
            ranged_attack=ranged_attack,
            ranged_defense=ranged_defense,
            speed=speed,
            accuracy=accuracy,
            evasion=evasion,
            max_ap=max_ap,
            move_slots=move_slots,
            evolutions=evolutions,
            bestiary_index=bestiary_index,
            move_tags=move_tags,
            battle_sprite_path=battle_sprite_path,
            tape_upgrades=tape_upgrades,
            bestiary_bios=bestiary_bios,
        )

    @staticmethod
    def __parse_tape_upgrades(
        scene: gp.GDFile, section: gp.GDResourceSection
    ) -> List[Union[TapeUpgrade, str]]:
        tape_upgrade_ids = section["tape_upgrades"]
        tape_upgrades: List[Union[TapeUpgrade, str]] = []
        for upgrade in tape_upgrade_ids:
            sub_resource = scene.find_sub_resource(id=upgrade.id)
            if sub_resource is not None:
                tape_upgrades.append(TapeUpgrade.from_sub_resource(sub_resource))
                continue

            ext_resource = scene.find_ext_resource(id=upgrade.id)
            if ext_resource is not None:
                tape_upgrades.append(ext_resource.path)
                continue

            raise ValueError(f"Could not find tape upgrade with id={upgrade.id}")

        return tape_upgrades

    @staticmethod
    def __parse_elemental_types(
        scene: gp.GDFile, section: gp.GDResourceSection
    ) -> List[str]:
        elemental_types_raw = section["elemental_types"]
        elemental_types = []
        for raw_type in elemental_types_raw:
            ext_resource = scene.find_ext_resource(id=raw_type.id)
            assert ext_resource is not None

            elemental_type = ext_resource.path.split("/")[-1].split(".tres")[0]
            elemental_types.append(elemental_type)

        return elemental_types

    @staticmethod
    def __parse_evolutions(
        scene: gp.GDFile, section: gp.GDResourceSection
    ) -> List[Evolution]:
        evolution_resources = section["evolutions"]
        evolutions = []
        for sub_section in evolution_resources:
            sub_resource = scene.find_sub_resource(id=sub_section.id)
            assert sub_resource is not None

            name = sub_resource["resource_name"]

            evolved_form_raw = sub_resource["evolved_form"]
            ext_resource = scene.find_ext_resource(id=evolved_form_raw.id)
            assert ext_resource is not None
            evolved_form = ext_resource.path

            assert isinstance(name, str)

            evolutions.append(Evolution(name=name, evolved_form=evolved_form))

        return evolutions
