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
