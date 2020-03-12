"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""


class ICustomBatchBlockRenderer:

    def add(self, position, block, face):
        pass

    def remove(self, position, block, data, face):
        [e.delete() for e in data]


class ICustomDrawMethodRenderer:

    def draw(self, position, block):
        pass

