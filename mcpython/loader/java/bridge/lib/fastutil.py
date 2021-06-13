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


class Object2FloatMap(NativeClass):
    NAME = "it/unimi/dsi/fastutil/objects/Object2FloatMap"

    @native("put", "(Ljava/lang/Object;F)F")
    def put(self, instance, key, value):
        return value


class Byte2ObjectArrayMap(NativeClass):
    NAME = "it/unimi/dsi/fastutil/bytes/Byte2ObjectArrayMap"

    @native("<init>", "(I)V")
    def init(self, instance, size):
        instance.underlying = {}


class ObjectOpenHashSet(NativeClass):
    NAME = "it/unimi/dsi/fastutil/objects/ObjectOpenHashSet"

    @native("<init>", "()V")
    def init(self, instance):
        instance.underlying = set()
