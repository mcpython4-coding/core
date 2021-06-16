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
import typing

from mcpython.loader.java.Java import NativeClass, native


class EnumSet(NativeClass):
    NAME = "java/util/EnumSet"

    def create_instance(self):
        instance = super().create_instance()
        instance.underlying = set()
        return instance

    @native("noneOf", "(Ljava/lang/Class;)Ljava/util/EnumSet;")
    def noneOf(self, cls):
        return self.create_instance()

    @native("of", "(Ljava/lang/Enum;)Ljava/util/EnumSet;")
    def of(self, *_):
        return self.create_instance()

    @native("of", "(Ljava/lang/Enum;Ljava/lang/Enum;)Ljava/util/EnumSet;")
    def of2(self, *_):
        return self.create_instance()

    @native("clear", "()V")
    def clear(self, instance):
        instance.underlying.clear()

    @native("addAll", "(Ljava/util/Collection;[Ljava/lang/Object;)Z")
    def addAll(self, collection, objects):
        pass

    def iter_over_instance(self, instance) -> typing.Iterable:
        return instance.underlying

    @native("iterator", "()Ljava/util/Iterator;")
    def iterator(self, instance):
        return list(instance.underlying)

    @native("toArray", "([Ljava/lang/Object;)[Ljava/lang/Object;")
    def toArray(self, instance, array):
        return list(instance.underlying)
