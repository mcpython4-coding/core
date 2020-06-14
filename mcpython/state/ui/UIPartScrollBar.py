"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.state.ui.UIPart
from pyglet.window import key, mouse
import mcpython.ResourceLocator
import pyglet
import mcpython.util.texture
import PIL.Image


IMAGE = mcpython.ResourceLocator.read("assets/minecraft/textures/gui/container/creative_inventory/tabs.png", "pil")
scroll_active = mcpython.util.texture.to_pyglet_image(IMAGE.crop((233, 0, 243, 14)).resize((20, 28), PIL.Image.NEAREST))
scroll_inactive = mcpython.util.texture.to_pyglet_image(IMAGE.crop((244, 0, 255, 14)).resize(
    (20, 28), PIL.Image.NEAREST))


class UIScrollBar(mcpython.state.ui.UIPart.UIPart):
    def __init__(self, position: tuple, scroll_distance: int):
        super().__init__(position, (0, 0))
        self.selected = False
        self.bar_position = position
        self.bar_sprite = pyglet.sprite.Sprite(scroll_active)
        self.scroll_distance = scroll_distance

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:mouse:release", self.on_mouse_release)
        self.master[0].eventbus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw)

    def on_mouse_press(self, x, y, button, mod):
        if button != mouse.LEFT: return
        bx, by = self.bar_position
        if 0 <= x - bx <= 20 and 0 <= y - by <= 28:
            self.selected = True

    def on_mouse_release(self, x, y, button, mod): self.selected = False

    def on_mouse_drag(self, x, y, dx, dy, button, mod):
        if button == mouse.LEFT and self.selected:
            self.bar_position = (self.position[0], max(self.position[1], min(self.position[1]+self.scroll_distance, y)))

    def on_draw(self):
        self.bar_sprite.position = self.bar_position
        self.bar_sprite.draw()

    def get_status(self):
        pass

