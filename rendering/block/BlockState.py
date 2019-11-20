

class IBlockStateDecoder:
    @classmethod
    def is_valid(cls, data) -> bool:
        raise NotImplementedError()

    @classmethod
    def decode(cls, data):
        raise NotImplementedError()


class McDefaultDecoder(IBlockStateDecoder):
    pass


class McForgeDefaultDecoder(IBlockStateDecoder):
    pass


BLOCKSTATES_DECODERS = [McForgeDefaultDecoder, McDefaultDecoder]  # priority: first in list, first checked


class BlockState:
    pass


class BlockStateContainer:
    pass

