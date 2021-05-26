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
from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class BiomeColors(NativeClass):
    NAME = "net/minecraft/world/biome/BiomeColors"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {"field_180291_a": None, "field_180289_b": None, "field_180290_c": None}
        )


class Biomes(NativeClass):
    NAME = "net/minecraft/world/biome/Biomes"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "field_76771_b": None,
            "field_76772_c": None,
            "field_76769_d": None,
            "field_76770_e": None,
            "field_76767_f": None,
            "field_76768_g": None,
        }

    def get_static_attribute(self, name: str):
        if name in self.exposed_attributes:
            return self.exposed_attributes[name]
        print("missing biome key", name)
        return None
