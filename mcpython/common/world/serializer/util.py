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
from mcpython import shared


def chunk2region(cx, cz):
    # todo: move to util/math
    return round(cx) >> 5, round(cz) >> 5


async def access_region_data(
    save_file,
    dimension: int,
    region: tuple,
):
    if dimension not in shared.world.dimensions:
        return
    return await save_file.access_file_pickle_async(
        "dim/{}/{}_{}.region".format(dimension, *region)
    )


async def write_region_data(
    save_file,
    dimension: int,
    region,
    data,
):
    await save_file.dump_file_pickle_async("dim/{}/{}_{}.region".format(dimension, *region), data)
