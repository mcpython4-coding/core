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
from mcpython.loader.java.Java import NativeClass, native


class Collections(NativeClass):
    NAME = "java/util/Collections"

    @native("addAll", "(Ljava/util/Collection;[Ljava/lang/Object;)Z")
    def addAll(self, collection, objects):
        pass  # todo: implement

    @native("unmodifiableList", "(Ljava/util/List;)Ljava/util/List;")
    def unmodifiableList(self, array):
        return tuple(array)

    @native("unmodifiableSet", "(Ljava/util/Set;)Ljava/util/Set;")
    def unmodifiableSet(self, instance):
        return instance  # todo: make mutable

    @native("emptyList", "()Ljava/util/List;")
    def emptyList(self):
        return []

    @native("emptyMap", "()Ljava/util/Map;")
    def emptyMap(self):
        return {}
