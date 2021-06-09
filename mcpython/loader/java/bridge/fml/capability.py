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
from mcpython import logger, shared
from mcpython.loader.java.Java import NativeClass, native


class CapabilityManager(NativeClass):
    NAME = "net/minecraftforge/common/capabilities/CapabilityManager"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "INSTANCE": None,
        })

    @native("register", "(Ljava/lang/Class;Lnet/minecraftforge/common/capabilities/Capability$IStorage;Ljava/util/concurrent/Callable;)V")
    def register(self, instance, cls, storage, consumer):
        pass

