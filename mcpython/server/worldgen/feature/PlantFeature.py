"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature


class PlantFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    def __init__(self):
        self.plants = []

    def add_plant(self, plant: str, weight: int):
        self.plants.append((plant, weight))
        return self
