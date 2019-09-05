"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import block.IBlock
import texture.model.ModelHandler


class BlockHandler:
    """
    main registry for blocks & block injection classes
    """

    def __init__(self):
        """
        setting up the BlockHandler
        """

        self.blocks = {}  # a name -> blockclass map
        self.blockclasses = []  # a list of blockclasses
        self.injectionclasses = {}  # a name -> injection class map

    def register(self, obj):
        """
        register an new block / block injection class
        :param obj: the block / injection class to register
        """

        if issubclass(obj, block.Block.Block):  # check for block class
            obj.on_register(self)  # call event function
            self.blockclasses.append(obj)  # add it to registry
            name = obj.get_name()
            self.blocks[name] = self.blocks[name.split(":")[-1]] = obj
        elif issubclass(obj, block.IBlock.IBlock):
            self.injectionclasses[obj.get_extension_name()] = obj
        else:
            raise ValueError("can only cast "+str(block.Block.Block)+"-subclasses to valid blocks")

    def __call__(self, obj):
        """
        makes it possible to use @G.blockhandler-notations
        :param obj: the obj to register
        :return: the obj itself
        """
        self.register(obj)
        return obj


handler = G.blockhandler = BlockHandler()


def load():
    """
    loads all blocks that should be loaded
    """
    import block.BlockFactory
    block.BlockFactory.BlockFactory.from_directory("assets/factory/block")

    from . import (IFallingBlock)

    from . import (BlockGrassBlock, BlockDirt)

    block.BlockFactory.BlockFactory.load()
