import ResourceLocator
import os
import rendering.IRenderAbleComponent


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
            pass
        else:
            pass

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
                blockstate = decoder.decode(data, name)
                # todo: add to some registry


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

