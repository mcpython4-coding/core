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


class String(NativeClass):
    NAME = "java/lang/String"

    @native("equals", "(Ljava/lang/Object;)Z")
    def equals(self, instance, other):
        return instance == other


class StringBuilder(NativeClass):
    NAME = "java/lang/StringBuilder"

    @native("<init>", "()V")
    def init(self, instance):
        instance.underlying = []

    @native("append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;")
    def append(self, instance, text):
        instance.underlying.append(text)
        return instance

    @native("toString", "()Ljava/lang/String;")
    def toString(self, instance):
        return "".join(instance.underlying)
