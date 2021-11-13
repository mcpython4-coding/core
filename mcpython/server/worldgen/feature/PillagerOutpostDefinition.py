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
import random

import mcpython.server.worldgen.feature.IFeature
from mcpython import shared

POSSIBLE_STRUCTURES = [
    "data/minecraft/structures/pillager_outpost/watchtower.nbt",
    "data/minecraft/structures/pillager_outpost/feature_cage1.nbt",
    "data/minecraft/structures/pillager_outpost/feature_cage2.nbt",
    "data/minecraft/structures/pillager_outpost/feature_logs.nbt",
    "data/minecraft/structures/pillager_outpost/feature_targets.nbt",
    "data/minecraft/structures/pillager_outpost/feature_tent1.nbt",
    "data/minecraft/structures/pillager_outpost/feature_tent2.nbt",
]

from .NBTStructureHelper import StructureNBTHelper

STRUCTURES = [StructureNBTHelper.from_file(e) for e in POSSIBLE_STRUCTURES]


@shared.registry
class PillagerOutpostDefinition(mcpython.server.worldgen.feature.IFeature.IFeature):
    NAME = "minecraft:pillager_outpost_feature"

    @classmethod
    def place(cls, dimension, x, y, z, config):
        structure = random.choice(STRUCTURES)
        structure.place(dimension, x, y, z, config)

    @classmethod
    def place_array(cls, array, x: int, y: int, z: int, config):
        structure = random.choice(STRUCTURES)
        structure.place_array(array, x, y, z, config)
