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
from mcpython.common.block.AbstractBlock import AbstractBlock
from mcpython.common.block.Furnace import Smoker
from mcpython.common.world.datafixers.NetworkFixers import BlockDataFixer
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


class Furnace0_1Fixer(BlockDataFixer):
    """
    Fixes the migration of the "progress" attribute and others of the Furnace block from int to float
    Below are the two classes for the blast furnace and smoker blocks, as they are delivered from the
    furnace block
    """

    BLOCK_NAME = "minecraft:furnace"

    BEFORE_VERSION: int = 0
    AFTER_VERSION: int = 1

    @classmethod
    async def apply2stream(
        cls,
        target: AbstractBlock,
        source_buffer: ReadBuffer,
        target_buffer: WriteBuffer,
    ) -> bool:
        import mcpython.client.gui.ContainerRenderer

        await AbstractBlock.read_internal_for_migration(target, source_buffer)
        await mcpython.client.gui.ContainerRenderer.ContainerRenderer.read_from_network_buffer(
            target.inventory, source_buffer
        )

        await AbstractBlock.write_internal_for_migration(target, target_buffer)
        await mcpython.client.gui.ContainerRenderer.ContainerRenderer.write_to_network_buffer(
            target.inventory, target_buffer
        )

        target_buffer.write_float(source_buffer.read_int())
        target_buffer.write_float(source_buffer.read_int())
        target_buffer.write_float(source_buffer.read_int())
        target_buffer.write_float(source_buffer.read_float())
        target_buffer.write_float(source_buffer.read_int())

        await target_buffer.write_list(
            await source_buffer.collect_list(source_buffer.read_string),
            target_buffer.write_string,
        )

        return False


class BlastFurnace0_1Fixer(Furnace0_1Fixer):
    BLOCK_NAME = "minecraft:blast_furnace"


class Smoker0_1Fixer(Furnace0_1Fixer):
    BLOCK_NAME = "minecraft:smoker"
