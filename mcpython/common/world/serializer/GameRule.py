"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.world.datafixers.IDataFixer


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


@G.registry
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
            G.world.gamerule_handler.table[name].status.load(data[name])

    @classmethod
    def save(cls, data, save_file):
        data = {
            gamerule.NAME: gamerule.status.save()
            for gamerule in G.world.gamerule_handler.table.values()
        }
        save_file.dump_file_json("gamerules.json", data)
