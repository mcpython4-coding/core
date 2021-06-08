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


class Gson(NativeClass):
    NAME = "com/google/gson/Gson"


class GsonBuilder(NativeClass):
    NAME = "com/google/gson/GsonBuilder"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("setPrettyPrinting", "()Lcom/google/gson/GsonBuilder;")
    def setPrettyPrinting(self, instance):
        return instance

    @native("create", "()Lcom/google/gson/Gson;")
    def create(self, instance):
        return self.vm.get_class(
            Gson.NAME, version=self.internal_version
        ).create_instance()
