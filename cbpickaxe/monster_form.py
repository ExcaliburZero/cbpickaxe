"""
Classes related to monster forms (species).
"""
from dataclasses import dataclass
from typing import cast, IO, List, Optional, Union

import godot_parser as gp

from .misc_types import Color


@dataclass
class TapeUpgrade:
    """
    An activity that occurs when a monster tape reaches a specific grade level.
    """

    name: str  #: Internal name of the upgrade.
    add_slot: bool  #: If True, then the monster gets one additional sticker slot during this upgrade.
    sticker: str  #: res:// path to the sticker the player gets when this upgrade occurs.

    @staticmethod
    def from_sub_resource(
        scene: gp.GDFile, sub_resource: gp.GDSubResourceSection
    ) -> "TapeUpgrade":
        """
        Parses the given sub resource into a TapeUpgrade.
        """
        name = sub_resource["resource_name"]
        add_slot = sub_resource.get("add_slot", default=False)
        sticker_resource = sub_resource["sticker"]

        ext_resource = scene.find_ext_resource(id=sticker_resource.id)
        assert ext_resource is not None
        sticker = ext_resource.path

        assert isinstance(name, str)
        assert isinstance(add_slot, bool)
        assert isinstance(sticker, str)

        return TapeUpgrade(name=name, add_slot=add_slot, sticker=sticker)


@dataclass
class Evolution:
    """
    A remastering that a monster tape can undergo.
    """

    name: str  #: Internal name of the remaster. Typically the English name of the remastered form.
    evolved_form: str  #: res:// path to the monster form the monster will remaster into.
    required_tape_grade: int  #: Grade that the monster needs to be at in order to remaster. (typically 5)
    min_hour: float  #: Minimum in-game hour for the remaster to be able to occur. (minimum of 0.0)
    max_hour: float  #: Maximum in-game hour for the remaster to be able to occur. (maximum of 24.0)
    required_location: Optional[str]
    specialization: Optional[
        str
    ]  #: String ID of the specialization choice to have the monster engage in this remaster.
    is_secret: bool


@dataclass
class MonsterForm:
    """
    A monster form (species).
    """

    name: str  #: String ID of the name of the monster.
    swap_colors: List[Color]
    default_palette: List[Color]
    emission_palette: List[Color]
    battle_cry: Optional[str]  #: res:// path of the battle cry sound of the monster.
    elemental_types: List[
        str
    ]  #: Elemental types of the monster. Typically only one, but can be empty or have multiple.
    exp_yield: int  #: Value used in calculating the exp the monster yields when defeated in battle. (typically 40)
    require_dlc: str  #: DLC that the monster requires. Empty if no DLC is required.
    pronouns: int
    description: str  #: String ID of the monster's description.
    max_hp: int  #: Base max HP stat value.
    melee_attack: int  #: Base melee attack stat value.
    melee_defense: int  #: Base melee defense stat value.
    ranged_attack: int  #: Base ranged attack stat value.
    ranged_defense: int  #: Base ranged defense stat value.
    speed: int  #: Base speed stat value.
    accuracy: int  #: Base accuracy value. (typically 100)
    evasion: int  #: Base evasion value. (typically 100)
    max_ap: int  #: Maximum amount of AP the monster can have in battle.
    move_slots: int  #: Number of move slots the monster has at base grade.
    evolutions: List[Evolution]  #: List of remasters that the monster can undergo.
    bestiary_index: int  #: Bestiary index. Natural numbers for main-game monsters. -1 for DLC and mod-added monsters.
    move_tags: List[
        str
    ]  #: List of tags that the monster can equip moves of. (Note that all monsters can also equip stickers with the "all" tag, which is not included in this list)
    battle_sprite_path: str  #: res:// path to the monster's battle sprite animation file.
    tape_upgrades: List[
        Union[TapeUpgrade, str]
    ]  #: Events that occur when the monster form increases its grade.
    bestiary_bios: List[
        str
    ]  #: List of string ids for the monster's bestiary entries. Typically a list of two string ids.

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

                battle_cry = MonsterForm.__parse_battle_cry(scene, section)
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
            swap_colors=[Color.from_gp(color) for color in swap_colors],
            default_palette=[Color.from_gp(color) for color in default_palette],
            emission_palette=[Color.from_gp(color) for color in emission_palette],
            battle_cry=battle_cry,
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
            if isinstance(upgrade, gp.SubResource):
                sub_resource = scene.find_sub_resource(id=upgrade.id)
                assert sub_resource is not None

                tape_upgrades.append(TapeUpgrade.from_sub_resource(scene, sub_resource))
                continue
            elif isinstance(upgrade, gp.ExtResource):
                ext_resource = scene.find_ext_resource(id=upgrade.id)
                assert ext_resource is not None

                tape_upgrades.append(ext_resource.path)
                continue

            raise ValueError(f"Could not find tape upgrade with id={upgrade.id}")

        return tape_upgrades

    @staticmethod
    def __parse_battle_cry(
        scene: gp.GDFile, section: gp.GDResourceSection
    ) -> Optional[str]:
        battle_cry_raw = section.get("battle_cry", None)
        if battle_cry_raw is None:
            return None

        ext_resource = scene.find_ext_resource(id=battle_cry_raw.id)
        assert ext_resource is not None

        return ext_resource.path

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
            required_tape_grade = sub_resource["required_tape_grade"]
            min_hour = sub_resource["min_hour"]
            max_hour = sub_resource["max_hour"]
            required_location = sub_resource["required_location"]
            specialization = sub_resource["specialization"]
            is_secret = sub_resource["is_secret"]

            evolved_form_raw = sub_resource["evolved_form"]
            ext_resource = scene.find_ext_resource(id=evolved_form_raw.id)
            assert ext_resource is not None
            evolved_form = ext_resource.path

            assert isinstance(name, str)
            assert isinstance(required_tape_grade, int)
            assert isinstance(min_hour, float)
            assert isinstance(max_hour, float)
            assert isinstance(required_location, str)
            assert isinstance(specialization, str)
            assert isinstance(is_secret, bool)

            if required_location == "":
                required_location = None

            if specialization == "":
                specialization = None

            evolutions.append(
                Evolution(
                    name=name,
                    evolved_form=evolved_form,
                    required_tape_grade=required_tape_grade,
                    min_hour=min_hour,
                    max_hour=max_hour,
                    required_location=required_location,
                    specialization=specialization,
                    is_secret=is_secret,
                )
            )

        return evolutions
