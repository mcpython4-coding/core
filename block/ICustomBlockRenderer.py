"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""


class IStaticCustomBlockRenderer:
    @classmethod
    def show(cls, block, position, batches) -> list: raise NotImplementedError()

    @classmethod
    def is_using_beside_model(cls, block) -> False: return False


class IObjectedCustomBlockRenderer:
    def show(self, block, position, batches) -> list: raise NotImplementedError()

    def is_using_beside_model(self, block) -> False: return False


class ICustomBlockRenderer(IStaticCustomBlockRenderer): pass

