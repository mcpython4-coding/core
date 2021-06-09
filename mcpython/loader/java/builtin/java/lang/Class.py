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


class Class(NativeClass):
    NAME = "java/lang/Class"

    @native("isInstance", "(Ljava/lang/Object;)Z")
    def isInstance(self, instance, obj):
        return obj.get_class().is_subclass_of(instance.name)

    @native("getInterfaces", "()[Ljava/lang/Class;")
    def getInterfaces(self, instance):
        return [interface() for interface in instance.interfaces]

    @native("forName", "(Ljava/lang/String;)Ljava/lang/Class;")
    def forName(self, name: str):
        return self.vm.get_class(name, version=self.internal_version)

    @native("newInstance", "()Ljava/lang/Object;")
    def newInstance(self, cls):
        return cls.create_instance()
