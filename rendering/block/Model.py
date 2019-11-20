

class IModelDecoder:
    """
    base class for every model decoder
    """

    @classmethod
    def is_valid(cls, data) -> bool:
        raise NotImplementedError()

    @classmethod
    def to_model(cls, data):
        raise NotImplementedError()


class DefaultMcModelDecoder(IModelDecoder):
    pass


MODEL_DECODERS = [DefaultMcModelDecoder]  # priority: first in list, first checked


class Model:
    def __init__(self, name):
        pass


class ModelRevision:
    """
    an renderable instance of an Model containing information like rotation, relative position...
    """

