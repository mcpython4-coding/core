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

import mcpython.common.event.api
import mcpython.common.event.Registry


class IFactoryModifier:
    def __init__(self):
        self.subscriber = []

    def on_apply(
        self,
        target: typing.Callable[
            [typing.Any, mcpython.common.event.api.IRegistryContent],
            mcpython.common.event.api.IRegistryContent,
        ],
    ):
        self.subscriber.append(target)

    def apply(
        self,
        factory,
        instance: mcpython.common.event.api.IRegistryContent,
    ) -> mcpython.common.event.api.IRegistryContent:
        for target in self.subscriber:
            instance = target(factory, instance)
        return instance
