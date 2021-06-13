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


class HashMap(NativeClass):
    NAME = "java/util/HashMap"

    def create_instance(self):
        return {}

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("<init>", "(I)V")
    def init2(self, instance, size: int):
        pass

    @native("put", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def put(self, instance, key, value):
        return value

    @native("containsKey", "(Ljava/lang/Object;)Z")
    def containsKey(self, instance, key):
        return key in instance

    @native("get", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def get(self, instance, key):
        return instance[key]

    @native("keySet", "()Ljava/util/Set;")
    def keySet(self, instance):
        return set(instance.keys())
