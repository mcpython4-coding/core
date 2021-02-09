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
from mcpython.common.data.gen.DataGeneratorManager import (
    IDataGenerator,
    DataGeneratorInstance,
)


class TagGenerator(IDataGenerator):
    def __init__(self, group: str, override=False):
        self.group = group
        self.override = override
        self.affected = set()

    def add_affected(self, *affected):
        self.affected.update(affected)

    def dump(self, generator: "DataGeneratorInstance"):
        return {"replace": self.override, "values": list(self.affected)}

    def get_default_location(self, generator: "DataGeneratorInstance", name: str):
        namespace, name = (
            name.split(":")
            if name.count(":") == 1
            else (generator.default_namespace, name)
        )
        return "data/{}/tags/{}/{}.json".format(name, self.group, name)
