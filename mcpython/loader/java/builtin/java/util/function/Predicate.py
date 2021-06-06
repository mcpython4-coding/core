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


class Predicate(NativeClass):
    NAME = "java/util/function/Predicate"

    @native("and", "(Ljava/util/function/Predicate;)Ljava/util/function/Predicate;")
    def and_chain(self, this, other):
        instance = self.vm.get_class("java/util/function/Predicate$And").create_instance()
        instance.elements = [this, other]
        return instance


class AndPredicate(Predicate):
    NAME = "java/util/function/Predicate$And"

    def create_instance(self):
        instance = super().create_instance()
        instance.elements = []
        return instance

