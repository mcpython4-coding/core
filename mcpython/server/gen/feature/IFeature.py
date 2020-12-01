"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.common.event.Registry


class IFeature(mcpython.common.event.Registry.Registry):
    TYPE = "minecraft:generation_feature"

    @staticmethod
    def place(dimension, x: int, y: int, z: int, **config):
        pass
