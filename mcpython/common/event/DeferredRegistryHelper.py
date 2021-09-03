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
import typing

from mcpython import shared
from mcpython.common.event.api import AbstractRegistry, IRegistryContent


class DeferredRegistryPipe:
    """
    Base class for deferred registries
    """

    def __init__(self, registry: AbstractRegistry, modname: str = "minecraft"):
        if registry.phase is None:
            raise ValueError(
                "registry defines no phase to fill it in, so deferred registration does not work!"
            )

        self.registry = registry
        self.modname = modname

    def register_later(self, lazy: typing.Callable[[], IRegistryContent]):
        shared.mod_loader(self.modname, self.registry.phase)(
            lambda: self.registry.register(lazy())
        )

    def create_later(self, factory_instance):
        shared.mod_loader(self.modname, self.registry.phase)(
            lambda: factory_instance.finish()
        )
