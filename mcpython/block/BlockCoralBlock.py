"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.block.Block
import mcpython.factory.BlockFactory


class ICoralBlock(mcpython.block.Block.Block):
    """
    base class for every coral block
    """

    ENABLE_RANDOM_TICKS = True

    def on_random_update(self):
        # todo: add water check; not arrival as it is not implemented
        G.world.get_active_dimension().get_chunk_for_position(self.position).add_block(
            self.position, "{}:dead_{}".format(*self.NAME.split(":")))


@G.registry
class BrainCoralBlock(ICoralBlock):
    """
    class for brain coral block
    """

    NAME: str = "minecraft:brain_coral_block"


@G.registry
class BubbleCoralBlock(ICoralBlock):
    """
    class for bubble coral block
    """

    NAME: str = "minecraft:bubble_coral_block"


@G.registry
class FireCoralBlock(ICoralBlock):
    """
    class for fire coral block
    """

    NAME: str = "minecraft:fire_coral_block"


@G.registry
class HornCoralBlock(ICoralBlock):
    """
    class for horn coral block
    """

    NAME: str = "minecraft:horn_coral_block"


@G.registry
class TubeCoralBlock(ICoralBlock):
    """
    class for tube coral block
    """

    NAME: str = "minecraft:tube_coral_block"


# the dead variants
mcpython.factory.BlockFactory.BlockFactory().setName("minecraft:dead_brain_coral_block").finish()
mcpython.factory.BlockFactory.BlockFactory().setName("minecraft:dead_bubble_coral_block").finish()
mcpython.factory.BlockFactory.BlockFactory().setName("minecraft:dead_fire_coral_block").finish()
mcpython.factory.BlockFactory.BlockFactory().setName("minecraft:dead_horn_coral_block").finish()
mcpython.factory.BlockFactory.BlockFactory().setName("minecraft:dead_tube_coral_block").finish()


# todo: create factory function

