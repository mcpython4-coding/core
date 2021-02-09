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
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.General
from mcpython import shared


@shared.registry
class DataFixer7to8(mcpython.common.world.datafixers.IDataFixer.IStorageVersionFixer):
    NAME = "minecraft:fixer_7_to_8"
    FIXES_FROM = 7
    FIXES_TO = 8

    @classmethod
    def apply(cls, save_file, *args):
        save_file.apply_part_fixer(WorldGenInfo.NAME)


@shared.registry
class WorldGenInfo(mcpython.common.world.serializer.General.WorldGeneralFixer):
    NAME = "minecraft:fixer_7_to_8_part_1"

    @classmethod
    def fix(cls, save_file, data: dict) -> dict:
        data["world_gen_info"] = {
            "noise_implementation": "minecraft:open_simplex_noise",
            "chunk_generators": {"minecraft:overworld": "minecraft:default_overworld"},
            "seeds": {},
        }
        return data
