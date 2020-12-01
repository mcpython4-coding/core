"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.storage.serializer.IDataSerializer
from mcpython import globals as G
import mcpython.server.storage.datafixers.IDataFixer


class GameRuleFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer targeting one or more game-rule entries
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to

    @classmethod
    def fix(cls, savefile, data) -> dict:
        pass


class GameRuleRemovalFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    Fixer targeting the removal of game-rule data from the save files
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to


@G.registry
class GameRule(mcpython.server.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:gamerule"

    @classmethod
    def apply_part_fixer(cls, savefile, fixer):
        if issubclass(fixer, GameRuleFixer):
            data = savefile.access_file_json("gamerules.json")
            if data is None: return
            for name in data:
                if name in fixer.TARGET_GAMERULE_NAME:
                    data[name] = fixer.fix(savefile, data[name])
            savefile.dump_file_json("gamerules.json", data)
        elif issubclass(fixer, GameRuleRemovalFixer):
            data = savefile.access_file_json("gamerules.json")
            if data is None: return
            for name in data:
                if name in fixer.TARGET_GAMERULE_NAME:
                    del data[name]
            savefile.dump_file_json("gamerules.json", data)

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("gamerules.json")
        if data is None: pass
        for name in data:
            G.world.gamerulehandler.table[name].status.load(data[name])

    @classmethod
    def save(cls, data, savefile):
        data = {gamerule.NAME: gamerule.status.save() for gamerule in G.world.gamerulehandler.table.values()}
        savefile.dump_file_json("gamerules.json", data)

