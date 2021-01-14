"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.block.AbstractBlock
import mcpython.common.factory.BlockFactory


class ICoralBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    base class for every coral block
    """

    ENABLE_RANDOM_TICKS = True

    def on_random_update(self):
        # todo: add water check; not arrival as it is not implemented
        G.world.get_dimension_by_name(self.dimension).get_chunk_for_position(
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


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(BrainCoralBlock)
    G.registry.register(BubbleCoralBlock)
    G.registry.register(FireCoralBlock)
    G.registry.register(HornCoralBlock)
    G.registry.register(TubeCoralBlock)
    # the dead variants, todo: add attributes like hardness
    mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        "minecraft:dead_brain_coral_block"
    ).finish()
    mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        "minecraft:dead_bubble_coral_block"
    ).finish()
    mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        "minecraft:dead_fire_coral_block"
    ).finish()
    mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        "minecraft:dead_horn_coral_block"
    ).finish()
    mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        "minecraft:dead_tube_coral_block"
    ).finish()


# todo: create factory function
