"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython.common.data.gen.DataGeneratorManager import (
    DataGeneratorInstance,
    IDataGenerator,
)


class LanguageGenerator(IDataGenerator):
    def __init__(self, lang_name: str):
        self.lang_name = lang_name
        self.table = {}

    def add_key(self, key: str, value: str):
        self.table[key] = value
        return self

    def dump(self, generator: DataGeneratorInstance):
        return self.table

    def get_default_location(self, generator: DataGeneratorInstance, name: str):
        return (
            "assets/{}/lang/{}.json".format(*name.split(":"))
            if ":" in name
            else "assets/{}/lang/{}.json".format(generator.default_namespace, name)
        )
