"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import pyglet
import mcpython.client.rendering.MatrixStack


class CollectionGroup(pyglet.graphics.Group):
    """
    Group of groups
    """

    def __init__(self, *sub_groups):
        super().__init__()
        self.sub_groups = sub_groups

    def set_state(self):
        [group.set_state() for group in self.sub_groups]

    def unset_state(self):
        [group.unset_state() for group in self.sub_groups]


class MatrixStackGroup(pyglet.graphics.Group):
    """
    Group for holding an custom MatrixStack-instance
    """

    def __init__(self, stack: mcpython.client.rendering.MatrixStack.MatrixStack):
        super().__init__()
        self.stack = stack

    def set_state(self):
        self.stack.apply()

    def unset_state(self):
        pass

