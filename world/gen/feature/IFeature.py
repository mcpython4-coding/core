"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry


class IFeature(event.Registry.Registry):
    @staticmethod
    def place(dimension, x, y, z, **config):
        pass

