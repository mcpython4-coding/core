"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.world.datafixers.IDataFixer
from mcpython import shared


class GameRuleFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer targeting one or more game-rule entries
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to

    @classmethod
    def fix(cls, save_file, data) -> dict:
        pass


class GameRuleRemovalFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Fixer targeting the removal of game-rule data from the save files
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to


@shared.registry
class GameRule(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:gamerule"

    @classmethod
    def apply_part_fixer(cls, save_file, fixer):
        if issubclass(fixer, GameRuleFixer):
            data = save_file.access_file_json("gamerules.json")
            if data is None:
                return
            for name in data:
                if name in fixer.TARGET_GAMERULE_NAME:
                    data[name] = fixer.fix(save_file, data[name])
            save_file.dump_file_json("gamerules.json", data)
        elif issubclass(fixer, GameRuleRemovalFixer):
            data = save_file.access_file_json("gamerules.json")
            if data is None:
                return
            for name in data:
                if name in fixer.TARGET_GAMERULE_NAME:
                    del data[name]
            save_file.dump_file_json("gamerules.json", data)

    @classmethod
    def load(cls, save_file):
        data = save_file.access_file_json("gamerules.json")
        if data is None:
            pass
        for name in data:
            shared.world.gamerule_handler.table[name].status.load(data[name])

    @classmethod
    def save(cls, data, save_file):
        data = {
            gamerule.NAME: gamerule.status.save()
            for gamerule in shared.world.gamerule_handler.table.values()
        }
        save_file.dump_file_json("gamerules.json", data)
