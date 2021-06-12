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
from mcpython.loader.java.Java import JavaMethod, NativeClass, native
from mcpython.loader.java.JavaExceptionStack import StackCollectingException


class Function(NativeClass):
    NAME = "java/util/function/Function"

    @native("apply", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, instance, obj):
        if isinstance(instance, JavaMethod):
            import mcpython.loader.java.Runtime

            runtime = mcpython.loader.java.Runtime.Runtime()
            try:
                return runtime.run_method(instance, obj)
            except StackCollectingException as e:
                e.add_trace(
                    f"during apply()-ing java/util/function/Function on {instance} with {obj}"
                )
                raise
        elif callable(instance):
            try:
                return instance(obj)
            except StackCollectingException as e:
                e.add_trace(
                    f"during apply()-ing java/util/function/Function on {instance} with {obj}"
                )
                raise
        raise StackCollectingException("not callable").add_trace(
            str(instance)
        ).add_trace(str(obj))
