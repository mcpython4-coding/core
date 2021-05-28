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


class Effects(NativeClass):
    NAME = "net/minecraft/potion/Effects"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_76424_c": None,
            "field_76431_k": None,
            "field_180152_w": None,
            "field_76438_s": None,
            "field_76444_x": None,
            "field_76441_p": None,
            "field_76428_l": None,
            "field_188423_x": None,
            "field_189112_A": None,
            "field_76426_n": None,
        })

    @native("func_76403_b", "()Z")
    def func_76403_b(self, instance) -> bool:
        return False


class Effect(NativeClass):
    NAME = "net/minecraft/potion/Effect"

    @native("func_76403_b", "()Z")
    def func_76403_b(self, instance):
        return False

