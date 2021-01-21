"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

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
