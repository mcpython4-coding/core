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


class Method(NativeClass):
    NAME = "java/lang/reflect/Method"

    @native("getClass", "()Ljava/lang/Class;")
    def getClass(self, instance):
        return self

    @native("accept", "(Ljava/lang/Object;)V")
    def accept(self, instance, obj):
        instance(obj)

    @native("apply", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, instance, arg1, arg2):
        return instance(arg1, arg2)

    @native("apply", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, instance, arg):
        return instance(arg)
