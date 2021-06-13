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


class GlobalLootModifierSerializer(NativeClass):
    NAME = "net/minecraftforge/common/loot/GlobalLootModifierSerializer"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native(
        "setRegistryName", "(Lnet/minecraft/util/ResourceLocation;)Ljava/lang/Object;"
    )
    def setRegistryName(self, instance, name):
        return instance

    @native("getRegistryName", "()Lnet/minecraft/util/ResourceLocation;")
    def getRegistryName(self, *_):
        pass

    @native("toString", "()Ljava/lang/String;")
    def toString(self, instance):
        return str(instance)
