"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import pyglet
import PIL.Image
import mcpython.ResourceLoader
from mcpython import shared as G
import mcpython.util.texture
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class BackgroundHandler:
    batch = pyglet.graphics.Batch()
    objects = []
    background_raw: PIL.Image.Image = mcpython.ResourceLoader.read_image(
        "assets/minecraft/textures/gui/options_background.png"
    )
    background_size = (32, 32)
    background_image = mcpython.util.texture.to_pyglet_image(
        background_raw.resize(background_size, PIL.Image.NEAREST)
    )

    old_win_size = None

    @classmethod
    def recreate(cls, wx, wy):
        if cls.old_win_size == (wx, wy):
            return
        cls.old_win_size = (wx, wy)
        [obj.delete() for obj in cls.objects]
        cls.objects.clear()
        for x in range(wx // cls.background_size[0] + 1):
            for y in range(wy // cls.background_size[1] + 1):
                obj = pyglet.sprite.Sprite(cls.background_image, batch=cls.batch)
                obj.position = (x * cls.background_size[0], y * cls.background_size[1])
                cls.objects.append(obj)


@onlyInClient()
class StatePartConfigBackground(mcpython.client.state.StatePart.StatePart):
    def activate(self):
        super().activate()
        BackgroundHandler.recreate(*G.window.get_size())

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe("render:draw:2d:background", self.draw)
        self.master[0].eventbus.subscribe("user:window:resize", self.resize)

    def draw(self):
        BackgroundHandler.batch.draw()

    def resize(self, x, y):
        BackgroundHandler.recreate(x, y)
