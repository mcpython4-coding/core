import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from .AbstractStateRenderer import AbstractStateRenderer
from mcpython import shared


class ConfigBackgroundRenderer(AbstractStateRenderer):
    ASSIGNED_DRAW_STAGE = "render:draw:2d:background"

    def __init__(self):
        super().__init__()

        background_raw: PIL.Image.Image = mcpython.engine.ResourceLoader.read_image(
            "assets/minecraft/textures/gui/options_background.png"
        )
        self.background_image = mcpython.util.texture.to_pyglet_image(
            background_raw.resize((32, 32), PIL.Image.NEAREST)
        )
        self.objects = []

    def recreate(self, wx, wy):
        [obj.delete() for obj in self.objects]
        self.objects.clear()

        for x in range(wx // 32 + 1):
            for y in range(wy // 32 + 1):
                obj = pyglet.sprite.Sprite(self.background_image, batch=self.batch)
                obj.position = (x * 32, y * 32)
                self.objects.append(obj)

    def on_activate(self):
        self.recreate(*shared.window.get_size())

    def resize(self, width, height):
        self.recreate(width, height)

    def draw(self):
        super().draw()

