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


class StateContainer(NativeClass):
    NAME = "net/minecraft/state/StateContainer"

    @native("func_177621_b", "()Lnet/minecraft/state/StateHolder;")
    def func_177621_b(self, instance):
        return instance


class EquipmentSlotType(NativeClass):
    NAME = "net/minecraft/inventory/EquipmentSlotType"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "HEAD": 0,
                "CHEST": 1,
                "LEGS": 2,
                "FEET": 3,
            }
        )


class ContainerType(NativeClass):
    NAME = "net/minecraft/inventory/container/ContainerType"
