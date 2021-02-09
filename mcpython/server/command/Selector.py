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
import math
import random

from mcpython import shared
import mcpython.common.event.Registry


class Selector(mcpython.common.event.Registry.IRegistryContent):
    """
    Selector base class
    """

    TYPE = "minecraft:selector"

    @staticmethod
    def is_valid(entry) -> bool:
        raise NotImplementedError()

    @staticmethod
    def parse(entry, config):
        pass


def load():
    @shared.registry
    class SelfSelector(Selector):
        NAME = "minecraft:@s"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@s"

        @staticmethod
        def parse(entry, config):
            return [config.entity]

    @shared.registry
    class PlayerSelector(Selector):
        NAME = "minecraft:@p"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@p"

        @staticmethod
        def parse(entry, config):
            players = list(shared.world.players.values())
            if len(players) == 0:
                return []
            x, y, z = config.position
            players.sort(
                key=lambda player: math.sqrt(
                    (x - player.position[0]) ** 2
                    + (y - player.position[1]) ** 2
                    + (z + player.position[2]) ** 2
                )
            )
            return [players[0]]

    @shared.registry
    class RandomPlayerSelector(Selector):
        NAME = "minecraft:@r"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@r"

        @staticmethod
        def parse(entry, config):
            return [random.choice(list(shared.world.players.values()))]

    @shared.registry
    class AllPlayerSelector(Selector):
        NAME = "minecraft:@a"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@a"

        @staticmethod
        def parse(entry, config):
            return list(shared.world.players.values())

    @shared.registry
    class EntitySelector(Selector):
        NAME = "minecraft:@e"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry.startswith("@e")

        @staticmethod
        def parse(entry, config):
            if entry == "@e":
                return list(shared.entity_handler.entity_map.values())
            raise NotImplementedError()  # todo: implement
