"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartTextInput, UIPartScrollBar
import globals as G
import mcpython.util.math
from pyglet.window import key
import pyglet
import random
import mcpython.mod.ModMcpython
import mcpython.state.StatePartConfigBackground
import logger
import mcpython.chat.DataPack
import mcpython.state.StateWorldGeneration
import mcpython.state.StateWorldLoading


class StateWorldSelection(State.State):
    NAME = "minecraft:world_selection"

    def __init__(self):
        super().__init__()

    def get_parts(self) -> list:
        wx, wy = G.window.get_size()
        return [mcpython.state.StatePartConfigBackground.StatePartConfigBackground(),
                UIPartButton.UIPartButton((150, 20), "generate new", (105, 60), anchor_button="MM", anchor_window="MD",
                                          on_press=self.on_new_world_press),
                UIPartButton.UIPartButton((150, 20), "play!", (-105, 60), anchor_button="MM",
                                          anchor_window="MD", on_press=self.on_world_load_press),
                UIPartButton.UIPartButton((150, 20), "back", (-105, 20), anchor_window="MD", anchor_button="MM",
                                          on_press=self.on_back_press),
                UIPartScrollBar.UIScrollBar((wx-60, 80), wy-140)]

    def on_back_press(self, *_):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_new_world_press(self, *_):
        worldname = "New World"  # if self.parts[1].entered_text == "" else self.parts[1].entered_text
        G.world.setup_by_filename(worldname)
        G.statehandler.switch_to("minecraft:world_generation_config")

    def on_world_load_press(self, *_):
        G.world.cleanup()
        worldname = "New World" # if self.parts[1].entered_text == "" else self.parts[1].entered_text
        G.world.setup_by_filename(worldname)
        G.statehandler.switch_to("minecraft:world_loading")

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1., 1., 1., 1.)

    def activate(self):
        super().activate()
        for part in self.parts:
            if issubclass(type(part), UIPartTextInput.UIPartTextInput):
                part.reset()


worldselection = None


def create():
    global worldselection
    worldselection = StateWorldSelection()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

