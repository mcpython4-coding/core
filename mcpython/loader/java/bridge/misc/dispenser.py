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


class DefaultDispenseItemBehavior(NativeClass):
    NAME = "net/minecraft/dispenser/DefaultDispenseItemBehavior"

    @native("<init>", "()V")
    def init(self, instance):
        pass


class DispenserBlock(NativeClass):
    NAME = "net/minecraft/block/DispenserBlock"

    @native(
        "func_199774_a",
        "(Lnet/minecraft/util/IItemProvider;Lnet/minecraft/dispenser/IDispenseItemBehavior;)V",
    )
    def func_199774_a(self, provider, behaviour):
        pass
