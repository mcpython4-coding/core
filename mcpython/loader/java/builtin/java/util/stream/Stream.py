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


class Stream(NativeClass):
    NAME = "java/util/stream/Stream"

    @native("filter", "(Ljava/util/function/Predicate;)Ljava/util/stream/Stream;")
    def filter(self, instance, predicate):
        return instance

    @native("forEach", "(Ljava/util/function/Consumer;)V")
    def forEach(self, instance, consumer):
        try:
            for entry in instance:
                consumer.inner(entry)
        except TypeError:
            pass
