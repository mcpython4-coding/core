import rendering.block.BoxModel
import rendering.IRenderAbleComponent


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


class Model(rendering.IRenderAbleComponent.IRenderAbleComponent):
    def __init__(self, name):
        pass


class ModelRevision(rendering.IRenderAbleComponent.IRenderAbleComponentRevision):
    """
    an renderable instance of an Model containing information like rotation, relative position...
    """

