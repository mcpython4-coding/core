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
from mcpython.loader.java.JavaExceptionStack import StackCollectingException


class String(NativeClass):
    NAME = "java/lang/String"

    @native("equals", "(Ljava/lang/Object;)Z")
    def equals(self, instance, other):
        return instance == other

    @native("contains", "(Ljava/lang/CharSequence;)Z")
    def contains(self, instance, substring):
        return substring in instance

    @native("split", "(Ljava/lang/String;)[Ljava/lang/String;")
    def split(self, instance, at):
        return instance.split(at)

    @native("valueOf", "(I)Ljava/lang/String;")
    def valueOf(self, value):
        return str(value)

    @native("toLowerCase", "()Ljava/lang/String;")
    def toLowerCase(self, instance):
        return instance.lower()


class StringBuilder(NativeClass):
    NAME = "java/lang/StringBuilder"

    @native("<init>", "()V")
    def init(self, instance):
        instance.underlying = []

    @native("append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;")
    def append(self, instance, text):
        if instance is None:
            raise StackCollectingException("NullPointerException: self is null")

        instance.underlying.append(text)
        return instance

    @native("append", "(Z)Ljava/lang/StringBuilder;")
    def append2(self, instance, value):
        if instance is None:
            raise StackCollectingException("NullPointerException: self is null")

        instance.underlying.append(str(value).lower())
        return instance

    @native("toString", "()Ljava/lang/String;")
    def toString(self, instance):
        return "".join(instance.underlying)
