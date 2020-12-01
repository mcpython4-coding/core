"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""


class ICustomBatchBlockRenderer:
    def add(self, position, block, face):
        pass

    def remove(self, position, block, data, face):
        [e.delete() for e in data]


class ICustomDrawMethodRenderer:
    def draw(self, position, block):
        pass


class ICustomBlockVertexManager:
    def handle(self, block, vertices, face, blockstate):
        pass

