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
import time

import clipboard
import mcpython.common.data.Language
import mcpython.common.state.AbstractStatePart
import mcpython.util.opengl
import pyglet
import pyglet.window.key
from mcpython.engine.rendering.RenderingLayerManager import MIDDLE_GROUND
from mcpython.util.annotation import onlyInClient

from . import AbstractUIPart

ALL_PATTERN = None
INT_PATTERN = "-0123456789."
INT_PATTERN_POSITIVE = INT_PATTERN[1:]


class UIPartTextInput(AbstractUIPart.AbstractUIPart):
    def __init__(
        self,
        size,
        position,
        anchor_ti="LD",
        anchor_window="LD",
        pattern=ALL_PATTERN,
        default_text="",
        text_size=10,
        on_text_update=None,
        on_enter_press=None,
        empty_overlay_text="",
    ):
        super().__init__(
            position, size, anchor_element=anchor_ti, anchor_window=anchor_window
        )
        self.pattern = pattern
        self.default_text = self.entered_text = default_text
        self.text_size = text_size
        self.selected = False
        self.on_text_update = on_text_update
        self.on_enter_press = on_enter_press
        self.lable = pyglet.text.Label(color=(255, 255, 255, 255), anchor_y="center")
        self.empty_overlay_text = empty_overlay_text

        # self.update_lable()

    def update_lable(self):
        x, y = self.get_real_position()
        self.lable.x, self.lable.y = x + 5, y + self.bounding_box_size[1] // 2
        if not self.selected and self.entered_text == "":
            if self.empty_overlay_text != "":
                self.lable.text = mcpython.common.data.Language.translate(
                    self.empty_overlay_text
                )
                self.lable.color = (150, 150, 150, 255)
                self.lable.font_size = self.bounding_box_size[1] // 4
        else:
            self.lable.color = (255, 255, 255, 255)
            self.lable.font_size = self.bounding_box_size[1] // 3
            self.lable.text = self.entered_text + (
                " " if time.time() // 2 % 2 == 0 or not self.selected else "_"
            )
            while self.lable.content_height > self.bounding_box_size[0] - 6:
                self.lable.text = self.lable.text[1:]

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe(
            MIDDLE_GROUND.getRenderingEvent(), self.on_draw_2d
        )
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.master[0].eventbus.subscribe("user:keyboard:enter", self.on_text)

    def on_draw_2d(self):
        self.update_lable()
        x, y = self.get_real_position()
        sx, sy = self.bounding_box_size
        mcpython.util.opengl.draw_rectangle((x, y), (sx, sy))
        mcpython.util.opengl.draw_line_rectangle(
            (x + 2, y + 1), (sx - 3, sy - 3), color=(1.0, 1.0, 1.0)
        )
        self.lable.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        rx, ry = self.get_real_position()
        sx, sy = self.bounding_box_size
        if 0 <= x - rx <= sx and 0 <= y - ry <= sy:
            self.selected = True
        else:
            self.selected = False

    def on_key_press(self, key, mod):
        if self.selected:
            if key == pyglet.window.key.ESCAPE:
                self.selected = False
            elif key == pyglet.window.key.ENTER:
                self.selected = False
                if self.on_enter_press:
                    self.on_enter_press()
            elif key == 65288 and len(self.entered_text) > 0:  # BACK
                self.entered_text = self.entered_text[:-1]
            elif key == pyglet.window.key.C and mod & pyglet.window.key.MOD_CTRL:
                clipboard.copy(self.entered_text)
            elif key == pyglet.window.key.V and mod & pyglet.window.key.MOD_CTRL:
                self.on_text(clipboard.paste())

    def on_text(self, text: str):
        if self.selected and (self.pattern is None or text in self.pattern):
            self.entered_text += text
            if self.on_text_update:
                self.on_text_update()

    def reset(self):
        self.entered_text = self.default_text


class TextInputTabHandler(mcpython.common.state.AbstractStatePart.AbstractStatePart):
    def __init__(self, textinputs: list):
        super().__init__()
        self.textinputs = textinputs

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)

    def on_key_press(self, button, mod):
        if button == pyglet.window.key.TAB:
            for i, uiparttextinput in enumerate(self.textinputs):
                if uiparttextinput.selected:
                    uiparttextinput.selected = False
                    reindex = i + 1 if not mod & pyglet.window.key.MOD_SHIFT else i - 1
                    if reindex < 0:
                        reindex = len(self.textinputs) - 1
                    if reindex >= len(self.textinputs):
                        reindex = 0
                    self.textinputs[reindex].selected = True
                    return
            self.textinputs[0].selected = True
