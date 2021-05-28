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


class HashMultiMap(NativeClass):
    NAME = "com/google/common/collect/HashMultimap"

    @native("create", "()Lcom/google/common/collect/HashMultimap;")
    def create(self):
        instance = self.create_instance()
        return instance


class Lists(NativeClass):
    NAME = "com/google/common/collect/Lists"

    @native("newArrayList", "()Ljava/util/ArrayList;")
    def create(self):
        instance = self.vm.get_class("java/util/ArrayList").create_instance()
        return instance


class Maps(NativeClass):
    NAME = "com/google/common/collect/Maps"

    @native("newHashMap", "()Ljava/util/HashMap;")
    def create(self):
        instance = self.vm.get_class("java/util/HashMap").create_instance()
        return instance

    @native("newHashMap", "(Ljava/util/Map;)Ljava/util/HashMap;")
    def copyHashMap(self, instance):
        return instance.copy()

    @native("newEnumMap", "(Ljava/util/Map;)Ljava/util/EnumMap;")
    def newEnumMap(self, base_map):
        return base_map


class ImmutableList(NativeClass):
    NAME = "com/google/common/collect/ImmutableList"

    def create_instance(self):
        instance = super().create_instance()
        instance.underlying_tuple = None
        return instance

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;[Ljava/lang/Object;)Lcom/google/common/collect/ImmutableList;",
    )
    def of(self, *stuff):
        instance = self.create_instance()
        instance.underlying_tuple = stuff[:-1] + tuple(stuff[-1])
        return instance

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableList;",
    )
    def of_2(self, *stuff):
        instance = self.create_instance()
        instance.underlying_tuple = stuff
        return instance


class ImmutableMap(NativeClass):
    NAME = "com/google/common/collect/ImmutableMap"

    @native("of", "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableMap;")
    def of(self, *stuff):
        return self.create_instance()
