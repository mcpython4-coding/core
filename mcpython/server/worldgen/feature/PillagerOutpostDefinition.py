"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


@shared.registry
class PillagerOutpostDefinition(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:pillager_outpost_feature"
