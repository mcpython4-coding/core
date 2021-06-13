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
from mcpython.loader.java.JavaExceptionStack import StackCollectingException


class Objects(NativeClass):
    NAME = "java/util/Objects"

    @native("requireNonNull", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def requireNonNull(self, obj):
        if obj is None:
            raise StackCollectingException("NullPointerException")
        return obj

    @native("nonNull", "(Ljava/lang/Object;)Z")
    def nonNull(self, obj):
        return int(obj is not None)
