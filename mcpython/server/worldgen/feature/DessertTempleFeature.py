"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


@shared.registry
class DessertTempleFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:dessert_temple_feature"
