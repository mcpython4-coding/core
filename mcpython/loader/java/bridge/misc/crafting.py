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


class IRecipeSerializer(NativeClass):
    NAME = "net/minecraft/item/crafting/IRecipeSerializer"


class IRecipeType(NativeClass):
    NAME = "net/minecraft/item/crafting/IRecipeType"

    @native(
        "func_222147_a", "(Ljava/lang/String;)Lnet/minecraft/item/crafting/IRecipeType;"
    )
    def func_222147_a(self, *_):
        return self.create_instance()
