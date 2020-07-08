"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import math
import random

import globals as G
import mcpython.event.Registry


class Selector(mcpython.event.Registry.IRegistryContent):
    """
    selector base class
    """

    TYPE = "minecraft:selector"

    @staticmethod
    def is_valid(entry) -> bool:
        raise NotImplementedError()

    @staticmethod
    def parse(entry, config):
        pass


def load():
    @G.registry
    class SelfSelector(Selector):
        NAME = "minecraft:@s"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@s"

        @staticmethod
        def parse(entry, config):
            return [config.entity]

    @G.registry
    class PlayerSelector(Selector):
        NAME = "minecraft:@p"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@p"

        @staticmethod
        def parse(entry, config):
            players = list(G.world.players.values())
            if len(players) == 0: return []
            x, y, z = config.position
            players.sort(key=lambda player: math.sqrt((x - player.position[0]) ** 2 + (y - player.position[1]) ** 2 +
                                                      (z + player.position[2]) ** 2))
            return [players[0]]

    @G.registry
    class RandomPlayerSelector(Selector):
        NAME = "minecraft:@r"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@r"

        @staticmethod
        def parse(entry, config):
            return [random.choice(list(G.world.players.values()))]

    @G.registry
    class AllPlayerSelector(Selector):
        NAME = "minecraft:@a"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@a"

        @staticmethod
        def parse(entry, config):
            return list(G.world.players.values())

    @G.registry
    class EntitySelector(Selector):
        NAME = "minecraft:@e"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry.startswith("@e")

        @staticmethod
        def parse(entry, config):
            if entry == "@e": return list(G.entityhandler.entity_map.values())
            raise NotImplementedError()  # todo: implement

