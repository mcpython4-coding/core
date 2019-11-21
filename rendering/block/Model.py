"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import rendering.IRenderAbleComponent
import event.Registry


class IModelDecoder:
    """
    base class for every model decoder
    """

    @classmethod
    def is_valid(cls, data, file) -> bool:
        raise NotImplementedError()

    @classmethod
    def to_model(cls, data, file):
        raise NotImplementedError()


class DefaultMcModelDecoder(IModelDecoder):
    @classmethod
    def is_valid(cls, data, file) -> bool: return file is None or file.endswith(".json")

    @classmethod
    def to_model(cls, data, file):
        raise NotImplementedError()


class DefaultOBJModelDecoder(IModelDecoder):
    @classmethod
    def is_valid(cls, data, file) -> bool: return file is None or file.endswith(".obj")

    @classmethod
    def to_model(cls, data, file):
        pass


class DefaultB3dModelDecoder(IModelDecoder):
    @classmethod
    def is_valid(cls, data, file) -> bool: return file is None or file.endswith(".b3d")

    @classmethod
    def to_model(cls, data, file):
        pass


MODEL_DECODERS = [DefaultMcModelDecoder]  # priority: first in list, first checked


class Model(rendering.IRenderAbleComponent.IRenderAbleComponent):
    @classmethod
    def from_mod(cls, modname: str):
        pass

    @classmethod
    def from_directory(cls, directory: str, include_sub_dirs=True):
        pass

    @classmethod
    def from_file(cls, file: str):
        pass

    @classmethod
    def from_data(cls, data, filename=None):
        for decoder in MODEL_DECODERS:
            if decoder.is_valid(data, filename):
                G.registry.register(decoder.to_model(data, filename))
                return

    def __init__(self, name):
        self.name = name

    def add_renderable_component(self, component):
        pass

    def get_revision(self, rotation):
        pass


class ModelRevision(rendering.IRenderAbleComponent.IRenderAbleComponentRevision):
    """
    an renderable instance of an Model containing information like rotation, relative position...
    """

    def add_to_batch(self, position, batch) -> list:
        pass


def on_register(registry, model):
    registry.get_attribute("models")[model.name] = model


modelregistry = event.Registry.Registry("modelregistry")
modelregistry.set_attribute("models", {})

