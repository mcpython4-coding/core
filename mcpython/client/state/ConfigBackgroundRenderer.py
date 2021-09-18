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

from ...engine.rendering.RenderingLayerManager import INTER_BACKGROUND
from .AbstractStateRenderer import AbstractStateRenderer


class ConfigBackgroundRenderer(AbstractStateRenderer):
    ASSIGNED_DRAW_STAGE = INTER_BACKGROUND.getRenderingEvent()

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
