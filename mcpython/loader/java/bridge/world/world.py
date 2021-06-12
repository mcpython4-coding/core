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


class World(NativeClass):
    NAME = "net/minecraft/world/World"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_234918_g_": None,
                "field_234919_h_": None,
                "field_234920_i_": None,
                "field_239699_ae_": None,
            }
        )
