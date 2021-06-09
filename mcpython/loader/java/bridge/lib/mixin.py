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


class LocalCapture(NativeClass):
    NAME = "org/spongepowered/asm/mixin/injection/callback/LocalCapture"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "CAPTURE_FAILSOFT": "org/spongepowered/asm/mixin/injection/callback/LocalCapture::CAPTURE_FAILSOFT",
            "CAPTURE_FAILHARD": "org/spongepowered/asm/mixin/injection/callback/LocalCapture::CAPTURE_FAILHARD",
        })


class At__Shift(NativeClass):
    NAME = "org/spongepowered/asm/mixin/injection/At$Shift"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "AFTER": "org/spongepowered/asm/mixin/injection/At$Shift::AFTER"
        })

