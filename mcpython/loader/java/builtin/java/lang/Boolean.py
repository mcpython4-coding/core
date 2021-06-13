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


class Boolean(NativeClass):
    NAME = "java/lang/Boolean"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "TRUE": 1,
                "FALSE": 0,
            }
        )

    @native("valueOf", "(Z)Ljava/lang/Boolean;")
    def valueOf(self, value):
        return value

    @native("toString", "(Z)Ljava/lang/String;")
    def toString(self, instance):
        return "true" if instance else "false"

    @native("parseBoolean", "(Ljava/lang/String;)Z")
    def parseBoolean(self, text: str):
        return int(text.lower() == "true")

    @native("booleanValue", "()Z")
    def booleanValue(self, instance):
        return instance
