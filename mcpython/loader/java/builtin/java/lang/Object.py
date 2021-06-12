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
import types

from mcpython.loader.java.Java import NativeClass, native


class Object(NativeClass):
    NAME = "java/lang/Object"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("getClass", "()Ljava/lang/Class;")
    def getClass(self, instance):
        if isinstance(
            instance, (types.FunctionType, types.MethodType, types.LambdaType)
        ):
            return self.vm.get_class(
                "java/lang/reflect/Method", version=self.internal_version
            )

        return instance.get_class()
