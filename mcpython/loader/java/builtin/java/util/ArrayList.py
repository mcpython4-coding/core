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


class ArrayList(NativeClass):
    NAME = "java/util/ArrayList"

    def create_instance(self):
        return []

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("<init>", "(Ljava/util/Collection;)V")
    def init2(self, instance, array):
        instance += array

    @native("size", "()I")
    def size(self, instance):
        return len(instance)

    @native("add", "(Ljava/lang/Object;)Z")
    def add(self, instance, obj):
        instance.append(obj)
        return 1
