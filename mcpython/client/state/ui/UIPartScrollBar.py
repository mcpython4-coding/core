"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import PIL.Image
import pyglet
from pyglet.window import mouse

import mcpython.ResourceLoader
import mcpython.util.texture
from mcpython.util.annotation import onlyInClient

IMAGE = mcpython.ResourceLoader.read_image(
    "assets/minecraft/textures/gui/container/creative_inventory/tabs.png"
)
scroll_active = mcpython.util.texture.to_pyglet_image(
    IMAGE.crop((233, 0, 243, 14)).resize((20, 28), PIL.Image.NEAREST)
)
scroll_inactive = mcpython.util.texture.to_pyglet_image(
    IMAGE.crop((244, 0, 255, 14)).resize((20, 28), PIL.Image.NEAREST)
)


@onlyInClient()
class UIScrollBar(mcpython.client.state.ui.UIPart.UIPart):
    """
    class representing an scroll bar
    """

    def __init__(self, position: tuple, scroll_distance: int, on_scroll=None):
        super().__init__(position, (0, 0))
        self.selected = False
        self.bar_position = position
        self.bar_sprite = pyglet.sprite.Sprite(scroll_active)
        self.scroll_distance = scroll_distance
        self.on_scroll = on_scroll
        self.active = True

    def move(self, delta: int):
        x, y = self.bar_position
        self.bar_position = x, max(
            self.position[1], min(self.position[1] + self.scroll_distance, y + delta)
        )
        if self.on_scroll:
            self.on_scroll(0, 0, 0, delta, 0, 0, self.get_status())

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:mouse:release", self.on_mouse_release)
        self.master[0].eventbus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw)

    def on_mouse_press(self, x, y, button, mod):
        if not self.active:
            return
        if button != mouse.LEFT:
            return
        bx, by = self.bar_position
        if 0 <= x - bx <= 20 and 0 <= y - by <= 28:
            self.selected = True

    def on_mouse_release(self, x, y, button, mod):
        self.selected = False

    def on_mouse_drag(self, x, y, dx, dy, button, mod):
        if not self.active:
            return
        if button == mouse.LEFT and self.selected:
            self.bar_position = (
                self.position[0],
                max(self.position[1], min(self.position[1] + self.scroll_distance, y)),
            )
            if self.on_scroll:
                self.on_scroll(x, y, dx, dy, button, mod, self.get_status())

    def on_draw(self):
        if not self.active:
            return
        self.bar_sprite.position = self.bar_position
        self.bar_sprite.draw()

    def get_status(self) -> float:
        """
        will return the status as an float between 0 and 1 where 0 is the downer end and 1 the upper
        """
        if not self.active:
            return 0
        return (self.bar_position[1] - self.position[1]) / self.scroll_distance

    def set_status(self, status: float):
        self.bar_position = (
            self.bar_position[0],
            self.position[1] + status * self.scroll_distance,
        )

    def set_size_respective(self, position: tuple, scroll_distance: int):
        if not self.active:
            return
        status = self.get_status()
        self.position = position
        self.bar_position = (
            self.position[0],
            self.position[1] + status * scroll_distance,
        )
        self.scroll_distance = scroll_distance
