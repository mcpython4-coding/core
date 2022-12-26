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
import pyglet
from mcpython import shared
from mcpython.util import opengl
from pyglet.window import key, mouse


class SearchBar:
    def __init__(
        self,
        change_callback=None,
        enter_callback=None,
        exit_callback=None,
        enable_mouse_to_enter=False,
    ):
        self.change_callback = change_callback
        self.enter_callback = enter_callback
        self.exit_callback = exit_callback

        self.position = 0, 0
        self.entry_size = 1, 1

        self.underlying_event_bus: mcpython.engine.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)
        self.underlying_event_bus.subscribe("user:keyboard:enter", self.on_text)
        self.underlying_event_bus.subscribe("user:mouse:press", self.on_mouse_press)

        self.enable_mouse_to_enter = enable_mouse_to_enter

        self.inner_text = ""
        self.enabled = False

        self.label = pyglet.text.Label()

    def close(self):
        self.inner_text = ""
        self.disable()

    def on_key_press(self, symbol, mod):
        if symbol == key.BACKSPACE and len(self.inner_text) > 0:
            self.inner_text = self.inner_text[:-1]
            self.change_callback(self.inner_text)
        elif symbol == key.ENTER:
            self.enter_callback()
        elif symbol == key.ESCAPE:
            self.exit_callback()

    def on_text(self, text: str):
        self.inner_text += text
        self.change_callback(self.inner_text)

    def on_mouse_press(self, x, y, button, mod):
        if (
            button == mouse.LEFT
            and self.enable_mouse_to_enter
            and self.is_position_in_field(x, y)
        ):
            self.enable()

    def enable(self):
        if shared.state_handler.global_key_bind_toggle:
            return
        if self.enabled:
            return
        self.enabled = True
        self.underlying_event_bus.activate()
        shared.state_handler.global_key_bind_toggle = True

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        self.underlying_event_bus.deactivate()
        shared.state_handler.global_key_bind_toggle = False

    def draw(self):
        self.label.font_size = self.entry_size[1] - 4
        self.label.text = self.inner_text
        while self.label.content_width > self.entry_size[0] - 4:
            self.label.text = self.label.text[1:]
        self.label.position = (self.position[0] + 2, self.position[1] + 2)
        self.label.draw()

        opengl.draw_line_rectangle(self.position, self.entry_size, (1, 0, 0, 1))

    def is_position_in_field(self, x: int, y: int):
        return (
            0 <= x - self.position[0] <= self.entry_size[0]
            and 0 <= y - self.position[1] <= self.entry_size[1]
        )
