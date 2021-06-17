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
from mcpython.loader.java.Java import NativeClass, native, NativeClassInstance


class Enum(NativeClass):
    NAME = "java/lang/Enum"

    @native("<init>", "(Ljava/lang/String;I)V")
    def init(self, instance, name: str, value: int):
        instance.name = name
        instance.ordinal = value

    @native("ordinal", "()I")
    def ordinal(self, instance):
        # todo: can we optimise this?
        if hasattr(instance, "get_class"):
            cls = instance.get_class()

            for key, value in cls.static_field_values.items():
                if value == instance:
                    return [i for i, e in enumerate(cls.enum_fields) if e.name == key][0]

            return cls.enum_fields.index(instance)

        return id(instance)

    @native("name", "()Ljava/lang/String;")
    def name2(self, instance):
        # todo: can we optimise this?
        if hasattr(instance, "get_class"):
            cls = instance.get_class()

            for key, value in cls.static_field_values.items():
                if value == instance:
                    return key

        return str(instance)

    @native("toString", "()Ljava/lang/String;")
    def toString(self, instance):
        return str(instance)
