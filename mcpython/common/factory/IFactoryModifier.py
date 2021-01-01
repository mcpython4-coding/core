"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.Registry


class IFactory:
    pass


class IFactoryModifier:
    def __init__(self):
        self.subscriber = []

    def on_apply(
        self,
        target: typing.Callable[
            [IFactory, mcpython.common.event.Registry.IRegistryContent],
            mcpython.common.event.Registry.IRegistryContent,
        ],
    ):
        self.subscriber.append(target)

    def apply(
        self,
        factory: IFactory,
        instance: mcpython.common.event.Registry.IRegistryContent,
    ) -> mcpython.common.event.Registry.IRegistryContent:
        for target in self.subscriber:
            instance = target(factory, instance)
        return instance
