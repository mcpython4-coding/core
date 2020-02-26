import globals as G
import block.Block
import factory.BlockFactory


class ICoralBlock(block.Block.Block):
    def on_random_update(self):
        # todo: add water check
        G.world.get_active_dimension().add_block(self.position, "{}:dead_{}".format(*self.NAME.split(":")))


@G.registry
class BrainCoralBlock(ICoralBlock):
     NAME = "minecraft:brain_coral_block"


@G.registry
class BubbleCoralBlock(ICoralBlock):
    NAME = "minecraft:bubble_coral_block"


@G.registry
class FireCoralBlock(ICoralBlock):
    NAME = "minecraft:fire_coral_block"


@G.registry
class HornCoralBlock(ICoralBlock):
    NAME = "minecraft:horn_coral_block"


@G.registry
class TubeCoralBlock(ICoralBlock):
    NAME = "minecraft:tube_coral_block"


factory.BlockFactory.BlockFactory().setName("minecraft:dead_brain_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_bubble_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_fire_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_horn_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_tube_coral_block").finish()

