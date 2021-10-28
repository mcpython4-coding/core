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
import mcpython.common.block.AbstractBlock
import mcpython.util.enums
from mcpython import shared


class ICoralBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    base class for every coral block
    """

    ENABLE_RANDOM_TICKS = True

    HARDNESS = 1.5
    BLAST_RESISTANCE = 6
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}

    def on_random_update(self):
        # todo: add water check; not arrival as it is not implemented
        shared.world.get_dimension_by_name(self.dimension).get_chunk_for_position(
            self.position
        ).add_block(self.position, "{}:dead_{}".format(*self.NAME.split(":")))


class BrainCoralBlock(ICoralBlock):
    """
    class for brain coral block
    """

    NAME: str = "minecraft:brain_coral_block"


class BubbleCoralBlock(ICoralBlock):
    """
    class for bubble coral block
    """

    NAME: str = "minecraft:bubble_coral_block"


class FireCoralBlock(ICoralBlock):
    """
    class for fire coral block
    """

    NAME: str = "minecraft:fire_coral_block"


class HornCoralBlock(ICoralBlock):
    """
    class for horn coral block
    """

    NAME: str = "minecraft:horn_coral_block"


class TubeCoralBlock(ICoralBlock):
    """
    class for tube coral block
    """

    NAME: str = "minecraft:tube_coral_block"


def load():
    from mcpython.common.factory.BlockFactory import BlockFactory

    # the dead variants, todo: add attributes like hardness
    BlockFactory().set_name("minecraft:dead_brain_coral_block").set_assigned_tools(
        mcpython.util.enums.ToolType.PICKAXE
    ).finish()
    BlockFactory().set_name("minecraft:dead_bubble_coral_block").set_assigned_tools(
        mcpython.util.enums.ToolType.PICKAXE
    ).finish()
    BlockFactory().set_name("minecraft:dead_fire_coral_block").set_assigned_tools(
        mcpython.util.enums.ToolType.PICKAXE
    ).finish()
    BlockFactory().set_name("minecraft:dead_horn_coral_block").set_assigned_tools(
        mcpython.util.enums.ToolType.PICKAXE
    ).finish()
    BlockFactory().set_name("minecraft:dead_tube_coral_block").set_assigned_tools(
        mcpython.util.enums.ToolType.PICKAXE
    ).finish()


# todo: create factory function
