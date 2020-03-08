"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartTextInput
from .ui.UIPartTextInput import INT_PATTERN
import globals as G
import util.math
from pyglet.window import key
import pyglet
import random
import mod.ModMcpython
import state.StatePartConfigBackground
import logger
import chat.DataPack
import state.StateWorldGeneration
import state.StateWorldLoading
import os
import shutil


class StateWorldSelection(State.State):
    NAME = "minecraft:world_selection"

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [state.StatePartConfigBackground.StatePartConfigBackground(),
                UIPartTextInput.UIPartTextInput((310, 30), (0, 80), anchor_ti="MM", anchor_window="MD",
                                                empty_overlay_text="world name: "),
                UIPartButton.UIPartButton((150, 30), "generate new", (-105, 40), anchor_button="MM", anchor_window="MD",
                                          on_press=self.on_new_world_press),
                UIPartButton.UIPartButton((150, 30), "load world", (105, 40), anchor_button="MM", anchor_window="MD",
                                          on_press=self.on_world_load_press),
                UIPartButton.UIPartButton((310, 30), "back", (0, 120), anchor_window="MD", anchor_button="MM",
                                          on_press=self.on_back_press)]

    def on_back_press(self, *_):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_new_world_press(self, *_):
        worldname = "New World" if self.parts[1].entered_text == "" else self.parts[1].entered_text
        if os.path.exists(G.local+"/saves/{}".format(worldname)):
            logger.println("deleting old world...")
            shutil.rmtree(G.local+"/saves/{}".format(worldname))
        G.world.setup_by_filename(worldname)
        G.statehandler.switch_to("minecraft:world_generation_config")

    def on_world_load_press(self, *_):
        G.world.cleanup()
        worldname = "New World" if self.parts[1].entered_text == "" else self.parts[1].entered_text
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

    def on_activate(self):
        for part in self.parts:
            if issubclass(type(part), UIPartTextInput.UIPartTextInput):
                part.reset()


worldselection = None


def create():
    global worldselection
    worldselection = StateWorldSelection()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

