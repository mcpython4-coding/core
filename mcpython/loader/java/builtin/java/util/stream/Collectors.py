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


class Collectors(NativeClass):
    NAME = "java/util/stream/Collectors"

    @native(
        "toMap",
        "(Ljava/util/function/Function;Ljava/util/function/Function;)Ljava/util/stream/Collector;",
    )
    def toMap(self, function1, function2):
        pass

    @native("toList", "()Ljava/util/stream/Collector;")
    def toList(self, collector):
        return collector

    @native("groupingBy", "(Ljava/util/function/Function;)Ljava/util/stream/Collector;")
    def groupingBy(self, function):
        def work(instance):
            data = {}
            for e in instance:
                data.setdefault(function(e), []).append(e)
            return data

        return work
