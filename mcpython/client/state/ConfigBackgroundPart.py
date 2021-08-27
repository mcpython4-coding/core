"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class BackgroundHandler:
    batch = pyglet.graphics.Batch()
    objects = []
    background_raw: PIL.Image.Image = mcpython.engine.ResourceLoader.read_image(
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
class ConfigBackground(mcpython.client.state.AbstractStatePart.AbstractStatePart):
    def activate(self):
        super().activate()
        BackgroundHandler.recreate(*shared.window.get_size())

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe("render:draw:2d:background", self.draw)
        self.master[0].eventbus.subscribe("user:window:resize", self.resize)

    def draw(self):
        BackgroundHandler.batch.draw()

    def resize(self, x, y):
        BackgroundHandler.recreate(x, y)
