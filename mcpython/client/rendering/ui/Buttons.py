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
import typing

import mcpython.engine.event.EventBus
import mcpython.engine.ResourceLoader
import pyglet
from mcpython import shared
from mcpython.client.rendering.ui.ButtonBackgroundBuilder import (
    ButtonState,
    DefaultButtonTexture,
)
from pyglet.window import key, mouse


class ImageOverlayButtonRenderer:
    def __init__(
        self,
        button_size: typing.Tuple[int, int],
        icon: pyglet.image.AbstractImage,
        on_press: typing.Callable,
        icon_offset=(0, 0),
    ):
        self.backgrounds = (
            DefaultButtonTexture.get_pyglet_texture(*button_size, ButtonState.ACTIVE),
            DefaultButtonTexture.get_pyglet_texture(*button_size, ButtonState.HOVERING),
            DefaultButtonTexture.get_pyglet_texture(*button_size, ButtonState.DISABLED),
        )
        self.icon = icon
        self.icon_offset = icon_offset
        self.on_press = on_press
        self.hovering = False
        self.active = True
        self.position = 0, 0
        self.size = button_size

        self.underlying_event_bus: mcpython.engine.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )
        self.underlying_event_bus.subscribe("user:mouse:motion", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)
        self.underlying_event_bus.subscribe("user:mouse:press", self.on_mouse_press)

    def on_mouse_move(self, x, y, dx, dy):
        self.hovering = self.over_button(x, y)

    def on_key_press(self, button, mod):
        x, y = shared.window.mouse_position

        if self.over_button(x, y) and button == key.ENTER:
            self.press_button()

    def on_mouse_press(self, x, y, button, mod):
        if self.over_button(x, y) and button == mouse.LEFT:
            self.press_button()

    def press_button(self):
        self.on_press()

    def over_button(self, x: int, y: int):
        return (
            0 <= x - self.position[0] <= self.size[0]
            and 0 <= y - self.position[1] <= self.size[1]
        )

    def activate(self):
        self.hovering = self.over_button(*shared.window.mouse_position)
        self.underlying_event_bus.activate()

    def deactivate(self):
        self.underlying_event_bus.deactivate()

    def draw(self):
        if not self.active:
            self.backgrounds[2].blit(*self.position)
        elif self.hovering:
            self.backgrounds[1].blit(*self.position)
        else:
            self.backgrounds[0].blit(*self.position)

        self.icon.blit(
            self.position[0] + self.icon_offset[0],
            self.position[1] + self.icon_offset[1],
        )


ARROW_TEXTURE_SHEET = None
RIGHT_ARROW = None
LEFT_ARROW = None


# todo: add to reload handler
def reload():
    global ARROW_TEXTURE_SHEET, RIGHT_ARROW, LEFT_ARROW
    ARROW_TEXTURE_SHEET = mcpython.engine.ResourceLoader.read_pyglet_image(
        "minecraft:gui/recipe_book"
    )
    RIGHT_ARROW = ARROW_TEXTURE_SHEET.get_region(0, 32, 12, 17)
    LEFT_ARROW = ARROW_TEXTURE_SHEET.get_region(15, 32, 12, 17)


if not shared.IS_TEST_ENV:
    reload()


def arrow_button_left(position, callback):
    instance = ImageOverlayButtonRenderer((18, 18), LEFT_ARROW, callback, (3, 0))
    instance.position = position
    return instance


def arrow_button_right(position, callback):
    instance = ImageOverlayButtonRenderer((18, 18), RIGHT_ARROW, callback, (3, 0))
    instance.position = position
    return instance
