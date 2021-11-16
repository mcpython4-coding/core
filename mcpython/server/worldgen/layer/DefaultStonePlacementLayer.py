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
from mcpython.server.worldgen.layer.ILayer import ILayer, LayerConfig


@shared.world_generation_handler
class DefaultStonePlacementLayer(ILayer):
    """
    Layer code for placing the ground stone layer
    """

    DEPENDS_ON = ["minecraft:heightmap_default"]

    NAME = "minecraft:stone_default"

    @classmethod
    async def add_generate_functions_to_chunk(cls, config: LayerConfig, reference):
        chunk = reference.chunk
        heightmap = reference.chunk.get_map("minecraft:height_map")

        for x in range(chunk.position[0] * 16, chunk.position[0] * 16 + 16):
            for z in range(chunk.position[1] * 16, chunk.position[1] * 16 + 16):

                height = heightmap.get_at_xz(x, z)[0][1]
                reference.schedule_invoke(
                    cls.generate_xz, reference, x, z, config, height
                )

    @staticmethod
    def generate_xz(reference, x, z, config, height):
        for y in range(1, height + 1):
            if not reference.chunk.is_position_blocked((x, y, z)):
                reference.schedule_block_add(
                    (x, y, z), "minecraft:stone", immediate=False
                )
