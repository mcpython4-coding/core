"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.storage.serializer.IDataSerializer
import globals as G
import mcpython.world.GameRule


@G.registry
class GameRule(mcpython.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:gamerule"

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

