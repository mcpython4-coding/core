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


class CriteriaTriggers(NativeClass):
    NAME = "net/minecraft/advancements/CriteriaTriggers"

    @native(
        "func_192118_a",
        "(Lnet/minecraft/advancements/ICriterionTrigger;)Lnet/minecraft/advancements/ICriterionTrigger;",
        static=True,
    )
    def func_192118_a(self, instance):
        return instance


class ICriterionTrigger(NativeClass):
    NAME = "net/minecraft/advancements/ICriterionTrigger"
