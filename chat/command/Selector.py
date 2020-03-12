"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry


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
    class SelectorEmpty(SelfSelector):
        NAME = "minecraft:@"

        @staticmethod
        def is_valid(entry) -> bool: return entry == "@"

    @G.registry
    class PlayerSelector(Selector):
        NAME = "minecraft:@p"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@p"

        @staticmethod
        def parse(entry, config):
            return [G.world.get_active_player()]

    # todo: fully implement
    @G.registry
    class RandomPlayerSelector(Selector):
        NAME = "minecraft:@r"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@r"

        @staticmethod
        def parse(entry, config):
            return [G.world.get_active_player()]

    @G.registry
    class AllPlayerSelector(Selector):
        NAME = "minecraft:@a"

        @staticmethod
        def is_valid(entry) -> bool:
            return entry == "@a"

        @staticmethod
        def parse(entry, config):
            return [G.world.get_active_player()]

