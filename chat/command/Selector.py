"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry
import math
import random


class Selector(event.Registry.IRegistryContent):
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

