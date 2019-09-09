"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import block.IBlock
import event.Registry


def register_block(registry, blockclass):
    if issubclass(blockclass, block.Block.Block):
        blockclass.on_register(block_registry)  # call event function
        name = blockclass.get_name()
        block_registry.get_attribute("blocks")[name] = block_registry.get_attribute("blocks")[name.split(":")[-1]] = \
            blockclass
        return
    elif issubclass(blockclass, block.IBlock.IBlock):
        block_registry.get_attribute("injectionclasses")[blockclass.get_extension_name()] = blockclass
    registry.registered_objects.remove(blockclass)  # todo: when registry is seperated, remove this


block_registry = event.Registry.Registry("block", inject_base_classes=[block.Block.Block, block.IBlock.IBlock],
                                         injection_function=register_block)
block_registry.set_attribute("blocks", {})
block_registry.set_attribute("injectionclasses", {})


def load():
    """
    loads all blocks that should be loaded
    """
    import block.BlockFactory
    block.BlockFactory.BlockFactory.from_directory("assets/factory/block")

    from . import (IFallingBlock, ILog)

    from . import (BlockGrassBlock, BlockDirt, BlockOakLog, BlockSpruceLog, BlockBirchLog, BlockJungleLog,
                   BlockAcaciaLog, BlockDarkOakLog)

    block.BlockFactory.BlockFactory.load()
