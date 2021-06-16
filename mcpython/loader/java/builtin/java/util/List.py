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


class List(NativeClass):
    NAME = "java/util/List"

    def create_instance(self):
        return []

    @native("add", "(Ljava/lang/Object;)Z")
    def add(self, instance, item):
        instance.append(item)
        return True

    @native("iterator", "()Ljava/util/Iterator;")
    def iterator(self, instance):
        return instance

    @native("forEach", "(Ljava/util/function/Consumer;)V")
    def forEach(self, instance, consumer):
        pass

    @native("addAll", "(Ljava/util/Collection;)Z")
    def addAll(self, instance, array):
        instance += array
        return 1
