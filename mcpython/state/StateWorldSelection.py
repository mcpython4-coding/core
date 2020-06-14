"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import datetime
import json
import os

import PIL.Image
import pyglet
from pyglet.window import key, mouse

import globals as G
import mcpython.ResourceLocator
import mcpython.chat.DataPack
import mcpython.mod.ModMcpython
import mcpython.state.StatePartConfigBackground
import mcpython.state.StateWorldGeneration
import mcpython.state.StateWorldLoading
import mcpython.storage.SaveFile
import mcpython.util.math
import mcpython.util.opengl
import mcpython.util.texture
from . import State
from .ui import UIPartButton, UIPartScrollBar

MISSING_TEXTURE = mcpython.util.texture.to_pyglet_image(
    mcpython.ResourceLocator.read("assets/missingtexture.png", "pil").resize((50, 50), PIL.Image.NEAREST))


class StateWorldSelection(State.State):
    NAME = "minecraft:world_selection"

    def __init__(self):
        super().__init__()
        self.world_data = []  # the data representing the world list; first goes first in list from above
        self.selected_world = None

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:overlay", self.on_draw_2d_post)
        self.eventbus.subscribe("user:window:resize", self.on_resize)

    def on_resize(self, wx, wy):
        self.parts[4].set_size_respective((wx - 60, 80), wy - 140)
        self.recalculate_sprite_position()

    def get_parts(self) -> list:
        wx, wy = G.window.get_size()
        return [mcpython.state.StatePartConfigBackground.StatePartConfigBackground(),
                UIPartButton.UIPartButton((150, 20), "generate new", (105, 60), anchor_button="MM", anchor_window="MD",
                                          on_press=self.on_new_world_press),
                UIPartButton.UIPartButton((150, 20), "play!", (-105, 60), anchor_button="MM",
                                          anchor_window="MD", on_press=self.on_world_load_press),
                UIPartButton.UIPartButton((150, 20), "back", (-105, 20), anchor_window="MD", anchor_button="MM",
                                          on_press=self.on_back_press),
                UIPartScrollBar.UIScrollBar((wx - 60, 80), wy - 140, on_scroll=self.on_scroll)]

    def on_mouse_press(self, x, y, button, modifiers):
        if not button == mouse.LEFT: return
        wx, _ = G.window.get_size()
        wx -= 120
        for i, (_, icon, _) in enumerate(self.world_data):
            px, py = icon.position
            if 0 <= x - px <= wx and 0 <= y - py <= 50:
                if 0 <= x - px <= 50:
                    self.enter_world(i)
                else:
                    if self.selected_world != i:
                        self.selected_world = i
                    else:
                        self.enter_world(i)
                return
        self.selected_world = None

    def on_scroll(self, x, y, dx, dy, button, mod, status):
        self.recalculate_sprite_position()

    def recalculate_sprite_position(self):
        wx, wy = G.window.get_size()
        status = (1-self.parts[4].get_status()) * len(self.world_data) * 60
        ay = wy - 60 + status - 160
        for i, (_, sprite, labels) in enumerate(self.world_data):
            sprite.x = 50
            sprite.y = ay
            dy = ay
            for label in labels:
                label.x = 120
                label.y = dy + 36
                dy -= 15
            ay -= 60

        if (wy - 140) / 60 > len(self.world_data):
            self.parts[4].active = False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)
        elif symbol == key.R:  # "R" will reload the world list
            self.reload_world_icons()
        elif symbol == key.ENTER and self.selected_world is not None:  # selecting world & pressing enter will launch it
            self.enter_world(self.selected_world)

    def on_draw_2d_post(self):
        wx, _ = G.window.get_size()
        pyglet.gl.glClearColor(1., 1., 1., 1.)
        for i, (_, icon, labels) in enumerate(self.world_data):
            icon.draw()
            for label in labels:
                label.draw()
            if i == self.selected_world:
                x, y = icon.position
                mcpython.util.opengl.draw_line_rectangle((x-2, y-2), (wx-116, 54), (1, 1, 1))

    def activate(self):
        super().activate()
        self.reload_world_icons()

    def reload_world_icons(self):
        self.world_data.clear()
        for directory in os.listdir(mcpython.storage.SaveFile.SAVE_DIRECTORY):
            path = os.path.join(mcpython.storage.SaveFile.SAVE_DIRECTORY, directory).replace("\\", "/")
            if os.path.isdir(path) and os.path.isfile(path+"/level.json"):
                if os.path.isfile(path+"/icon.png"):
                    icon = pyglet.image.load(path+"/icon.png")
                else:
                    icon = MISSING_TEXTURE
                sprite = pyglet.sprite.Sprite(icon)
                with open(path+"/level.json") as f:
                    data = json.load(f)
                edit_date = datetime.datetime.fromtimestamp(os.path.getmtime(path+"/level.json"))
                diff = datetime.datetime.now() - edit_date
                if diff.days < 5:
                    edit = "{} days ago".format(diff.days)
                else:
                    edit = "on {}".format(edit_date.isoformat())
                labels = [pyglet.text.Label(directory),
                          pyglet.text.Label("last played in version '{}' {}".format(
                              data["game version"], edit)),
                          pyglet.text.Label("last loaded with {} mod{}".format(
                              len(data["mods"]), "" if len(data["mods"]) <= 1 else "s"))]
                self.world_data.append((edit_date, sprite, labels))
        self.world_data.sort(key=lambda d: d[0].timestamp())
        self.recalculate_sprite_position()

    def on_back_press(self, *_):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_new_world_press(self, *_):
        G.statehandler.switch_to("minecraft:world_generation_config")

    def on_world_load_press(self, *_):
        if self.selected_world is None: return
        self.enter_world(self.selected_world)

    def enter_world(self, number: int):
        G.world.cleanup()
        G.world.setup_by_filename(self.world_data[number][2][0].text)
        G.statehandler.switch_to("minecraft:world_loading")


worldselection = None


def create():
    global worldselection
    worldselection = StateWorldSelection()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
