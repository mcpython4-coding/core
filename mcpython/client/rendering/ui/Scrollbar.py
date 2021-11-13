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

import mcpython.engine.event.EventHandler
from pyglet.window import key


class ScrollbarRenderer:
    def __init__(
        self,
        texture,
        position: typing.Tuple[int, int],
        height: int,
        steps: int,
        per_page_button=1,
        on_progress_change=None,
        enable_key_progress_changes=True,
    ):
        self.texture = texture
        self.position = position
        self.height = height
        self.steps = steps
        self.per_page_button = per_page_button
        self.current_step = 0
        self.on_progress_change = on_progress_change

        self.enable_key_progress_changes = enable_key_progress_changes

    def on_activate(self):
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_deactivate(self):
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_key_press(self, symbol, modifiers):
        if not self.enable_key_progress_changes:
            return

        if symbol == key.UP:
            if modifiers & key.MOD_CTRL:
                self.current_step = self.steps - 1
            else:
                self.current_step = min(self.current_step + 1, self.steps - 1)
        elif symbol == key.DOWN:
            if modifiers & key.MOD_CTRL:
                self.current_step = 0
            else:
                self.current_step = max(self.current_step - 1, 0)
        elif symbol == key.PAGEUP:
            self.current_step = min(
                self.current_step + self.per_page_button, self.steps - 1
            )
        elif symbol == key.PAGEDOWN:
            self.current_step = max(self.current_step - self.per_page_button, 0)
        else:
            return

        if self.on_progress_change:
            self.on_progress_change()

    def draw(self, offset: typing.Tuple[int, int]):
        x, y = self.position
        x += offset[0]
        y += offset[1]
        y += round(self.height * ((self.current_step + 1) / self.steps))

        self.texture.blit(x, y)
