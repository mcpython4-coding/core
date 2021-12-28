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
from .simple import CombinedFactoryInstance


async def create_full_slab_wall_set(
    name: str, texture: str, and_button=False
) -> CombinedFactoryInstance:
    instance = CombinedFactoryInstance(name, texture)
    await instance.create_full_block()
    await instance.create_slab_block(suffix=lambda n: n.removesuffix("s") + "_slab")
    await instance.create_wall(suffix=lambda n: n.removesuffix("s") + "_wall")
    if and_button:
        await instance.create_button_block(suffix=lambda n: n.removesuffix("s") + "_button")

    return instance
