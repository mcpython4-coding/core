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


@shared.registry
class GameRule(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:gamerule"

    @classmethod
    async def load(cls, save_file):
        data = save_file.access_file_json("gamerules.json")
        if data is None:
            pass

        for name in data:
            shared.world.gamerule_handler.table[name].status.load(data[name])

    @classmethod
    async def save(cls, data, save_file):
        data = {
            gamerule.NAME: gamerule.status.save()
            for gamerule in shared.world.gamerule_handler.table.values()
        }
        save_file.dump_file_json("gamerules.json", data)
