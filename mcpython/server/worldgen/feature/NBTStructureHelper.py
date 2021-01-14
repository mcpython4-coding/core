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
import python_nbt.nbt as nbt
import mcpython.ResourceLoader
from mcpython import shared


class StructureNBTHelper:
    @classmethod
    def from_file(cls, file: str):
        data = mcpython.ResourceLoader.read_raw(file)
        with open(shared.tmp.name + "/tmp.nbt", mode="wb") as f:
            f.write(data)
        return cls(nbt.read_from_nbt_file(shared.tmp.name + "/tmp.nbt").json_obj())

    def __init__(self, data: dict):
        pass
