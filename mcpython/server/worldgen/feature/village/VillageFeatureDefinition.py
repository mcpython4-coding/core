"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


@shared.registry
class VillageFeatureDefinitionPlains(
    mcpython.server.worldgen.feature.IFeature.IFeature
):
    NAME = "minecraft:plains_village_feature"


@shared.registry
class VillageFeatureDefinitionDessert(
    mcpython.server.worldgen.feature.IFeature.IFeature
):
    NAME = "minecraft:dessert_village_feature"
