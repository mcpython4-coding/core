import globals as G
import block.Block
import factory.BlockFactory


class ICoralBlock(block.Block.Block):
    def on_random_update(self):
        # todo: add water check
        G.world.get_active_dimension().add_block(self.position, "{}:dead_{}".format(*self.get_name().split(":")))


@G.registry
class BrainCoralBlock(ICoralBlock):
    @staticmethod
    def get_name(): return "minecraft:brain_coral_block"


@G.registry
class BubbleCoralBlock(ICoralBlock):
    @staticmethod
    def get_name(): return "minecraft:bubble_coral_block"


@G.registry
class FireCoralBlock(ICoralBlock):
    @staticmethod
    def get_name(): return "minecraft:fire_coral_block"


@G.registry
class HornCoralBlock(ICoralBlock):
    @staticmethod
    def get_name(): return "minecraft:horn_coral_block"


@G.registry
class TubeCoralBlock(ICoralBlock):
    @staticmethod
    def get_name(): return "minecraft:tube_coral_block"


factory.BlockFactory.BlockFactory().setName("minecraft:dead_brain_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_bubble_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_fire_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_horn_coral_block").finish()
factory.BlockFactory.BlockFactory().setName("minecraft:dead_tube_coral_block").finish()

