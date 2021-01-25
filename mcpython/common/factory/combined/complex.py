"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from .simple import CombinedFactoryInstance


def create_full_slab_wall_set(
    name: str, texture: str, and_button=False
) -> CombinedFactoryInstance:
    instance = (
        CombinedFactoryInstance(name, texture)
        .create_full_block()
        .create_slab_block(suffix=lambda n: n.removesuffix("s") + "_slab")
        .create_wall(suffix=lambda n: n.removesuffix("s") + "_wall")
    )
    if and_button:
        instance.create_button_block(suffix=lambda n: n.removesuffix("s") + "_button")
    return instance
