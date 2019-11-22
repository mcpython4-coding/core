"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import ResourceLocator
import os
import rendering.IRenderAbleComponent
import event.Registry


class IBlockStateDecoder:
    @classmethod
    def is_valid(cls, data) -> bool:
        raise NotImplementedError()

    @classmethod
    def decode(cls, data, name):
        raise NotImplementedError()


class McDefaultDecoder(IBlockStateDecoder):
    @classmethod
    def is_valid(cls, data) -> bool:
        return type(data) == dict and not any([("marker" in x) for x in data.keys()])

    @classmethod
    def decode(cls, data, name):
        states = {}


class McForgeDefaultDecoder(IBlockStateDecoder):
    """
    This is the decoder for the minecraft forge BlockState format.
    It supports only the version 1
    """
    @classmethod
    def is_valid(cls, data) -> bool:
        return type(data) == dict and "forge_marker" in data and data["forge_marker"] == 1

    @classmethod
    def decode(cls, data, name):
        states = {}


BLOCKSTATES_DECODERS = [McForgeDefaultDecoder, McDefaultDecoder]  # priority: first in list, first checked


class BlockState(rendering.IRenderAbleComponent.IRenderAbleComponent):
    def get_revision(self, rotation):
        raise NotImplementedError("BlockState can NOT create an sub-part based on rotation")

    @classmethod
    def from_mod(cls, modname: str):
        cls.from_directory("assets/{}/blockstates".format(modname))

    @classmethod
    def from_directory(cls, directory: str, include_sub_dirs=True):
        if include_sub_dirs:
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    cls.from_file(os.path.join(root, name))
        else:
            for name in os.listdir(directory):
                cls.from_file(os.path.join(directory, name))

    @classmethod
    def from_file(cls, file: str, modname=None, filename=None):
        if (modname is None or filename is None) and "blockstates" in file:
            s = file.split("/")
            i = s.index("blockstates")
            if modname is None: modname = s[i-1]
            if filename is None: filename = "/".join(s[i+1:])
        return cls.from_data(ResourceLocator.read(file, "json"), modname+"/"+filename)

    @classmethod
    def from_data(cls, data, name):
        for decoder in BLOCKSTATES_DECODERS:
            if decoder.is_valid(data):
                G.registry.register(decoder.decode(data, name))
                return

    def __init__(self, name):
        self.name = name


class IBlockStateContainer(rendering.IRenderAbleComponent.IRenderAbleComponentRevision):
    """
    Base class for every single state of an BlockState-file
    This is what in the end is callen to draw the block
    """

    def add_to_batch(self, position, batch) -> list:
        return []


class DefaultBlockStateContainer(IBlockStateContainer):
    """
    base class for every basic blockstate containing only an finite list of BoxModels and depending NOT on another state
    """


def add_blockstate(registry, blockstate):
    registry.get_attribute("table")[blockstate.name] = blockstate


blockstateutil = event.Registry.Registry(
    "blockstateutil", inject_base_classes=[IBlockStateContainer, IBlockStateDecoder])
blockstates = event.Registry.Registry("blockstates", injection_function=add_blockstate, inject_base_classes=[
    BlockState])
blockstates.set_attribute("table", {})

