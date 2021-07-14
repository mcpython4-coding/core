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
import mcpython.engine.ResourceLoader
import python_nbt.nbt as nbt
from mcpython import shared


class StructureNBTHelper:
    @classmethod
    def from_file(cls, file: str):
        data = mcpython.engine.ResourceLoader.read_raw(file)
        with open(shared.tmp.name + "/tmp.nbt", mode="wb") as f:
            f.write(data)
        return cls(nbt.read_from_nbt_file(shared.tmp.name + "/tmp.nbt").json_obj())

    def __init__(self, data: dict):
        pass
