"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""


class IRenderAbleComponent:
    def get_revision(self, rotation):
        raise NotImplementedError()


class IRenderAbleComponentRevision:
    def add_to_batch(self, position, batch) -> list:
        raise NotImplementedError()

