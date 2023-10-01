from dataclasses import dataclass
from typing import Dict, IO, List, Optional, Sequence, Union

import godot_parser as gp


@dataclass
class TapeUpgrade:
    name: str
    add_slot: bool

    @staticmethod
    def from_sub_resource(sub_resource: gp.GDSubResourceSection) -> "TapeUpgrade":
        name = sub_resource["resource_name"]
        add_slot = sub_resource.get("add_slot", default=False)

        assert isinstance(name, str)
        assert isinstance(add_slot, bool)

        return TapeUpgrade(name=name, add_slot=add_slot)


@dataclass
class MonsterForm:
    name: str
    bestiary_index: int
    move_slots: int
    tape_upgrades: List[Union[TapeUpgrade, str]]

    @property
    def max_move_slots(self) -> int:
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
        scene = gp.parse(input_stream.read())

        name = None
        move_slots = None
        tape_upgrades: Optional[Sequence[TapeUpgrade]] = None

        for section in scene.get_sections():
            if type(section) == gp.GDResourceSection:
                name = section["name"]
                bestiary_index = section["bestiary_index"]
                move_slots = section["move_slots"]

                tape_upgrade_ids = section["tape_upgrades"]
                tape_upgrades = []
                for upgrade in tape_upgrade_ids:
                    sub_resource = scene.find_sub_resource(id=upgrade.id)
                    if sub_resource is not None:
                        tape_upgrades.append(
                            TapeUpgrade.from_sub_resource(sub_resource)
                        )
                        continue

                    ext_resource = scene.find_ext_resource(id=upgrade.id)
                    if ext_resource is not None:
                        tape_upgrades.append(ext_resource.path)
                        continue

                    raise ValueError(
                        f"Could not find tape upgrade with id={upgrade.id}"
                    )

        assert isinstance(name, str)
        assert isinstance(bestiary_index, int)
        assert isinstance(move_slots, int)
        assert tape_upgrades is not None

        return MonsterForm(
            name=name,
            bestiary_index=bestiary_index,
            move_slots=move_slots,
            tape_upgrades=list(tape_upgrades),
        )


if __name__ == "__main__":
    with open("data/traffikrab.tres", "r") as input_stream:
        monster_form = MonsterForm.from_tres(input_stream)
        print(monster_form)
        print(monster_form.move_slots)
        print(monster_form.max_move_slots)
