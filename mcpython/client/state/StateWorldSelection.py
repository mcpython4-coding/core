"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import datetime
import json
import os

import PIL.Image
import pyglet
from pyglet.window import key, mouse

from mcpython import shared as G
import mcpython.ResourceLoader
import mcpython.common.DataPack
import mcpython.common.mod.ModMcpython
import mcpython.client.state.StatePartConfigBackground
import mcpython.client.state.StateWorldGeneration
import mcpython.client.state.StateWorldLoading
import mcpython.server.storage.SaveFile
import mcpython.util.math
import mcpython.util.opengl
import mcpython.util.texture
from . import State
from .ui import UIPartButton, UIPartScrollBar
import shutil
from mcpython.util.annotation import onlyInClient
import mcpython.client.rendering.RenderingGroups

MISSING_TEXTURE = mcpython.util.texture.to_pyglet_image(
    mcpython.ResourceLoader.read_image("assets/missing_texture.png").resize(
        (50, 50), PIL.Image.NEAREST
    )
)
WORLD_SELECTION = mcpython.ResourceLoader.read_image("minecraft:gui/world_selection")
WORLD_SELECTION_SELECT = mcpython.util.texture.to_pyglet_image(
    WORLD_SELECTION.crop((0, 0, 32, 32))
)


@onlyInClient()
class StateWorldSelection(State.State):
    NAME = "minecraft:world_selection"

    def __init__(self):
        super().__init__()
        self.world_data = (
            []
        )  # the data representing the world list; first goes first in list from above
        self.selected_world = None
        self.selection_sprite = pyglet.sprite.Sprite(WORLD_SELECTION_SELECT)
        del self.eventbus
        self.eventbus = G.event_handler.create_bus(active=False, crash_on_error=False)
        for statepart in self.parts:
            statepart.master = [
                self
            ]  # StateParts get an list of steps to get to them as an list
            statepart.bind_to_eventbus()  # Ok, you can now assign to these event bus
        self.bind_to_eventbus()
        self.scissor_group = mcpython.client.rendering.RenderingGroups.ScissorGroup(
            0, 0, 10, 10
        )

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:overlay", self.on_draw_2d_post)
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)

    def on_resize(self, wx, wy):
        self.parts[-1].set_size_respective((wx - 80, 105), wy - 195)
        self.recalculate_sprite_position()
        self.scissor_group.area = (45, 100, wx - 90, wy - 160)

    def get_parts(self) -> list:
        wx, wy = G.window.get_size()
        return [
            mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground(),
            UIPartButton.UIPartButton(
                (150, 20),
                "generate new",
                (105, 60),
                anchor_button="MM",
                anchor_window="MD",
                on_press=self.on_new_world_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "play!",
                (-105, 60),
                anchor_button="MM",
                anchor_window="MD",
                on_press=self.on_world_load_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "back",
                (-105, 20),
                anchor_window="MD",
                anchor_button="MD",
                on_press=self.on_back_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "delete",
                (105, 20),
                anchor_window="MD",
                anchor_button="MD",
                on_press=self.on_delete_press,
            ),
            UIPartScrollBar.UIScrollBar(
                (wx - 80, 105), wy - 195, on_scroll=self.on_scroll
            ),
        ]

    def on_mouse_press(self, x, y, button, modifiers):
        if not button == mouse.LEFT:
            return
        wx, _ = G.window.get_size()
        wx -= 120
        for i, (_, icon, _, _) in enumerate(self.world_data):
            px, py = icon.position
            if 0 <= x - px <= wx - 130 and 0 <= y - py <= 50:
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

    def on_mouse_scroll(self, x, y, dx, dy):
        self.parts[-1].move(dy * 4)

    def recalculate_sprite_position(self):
        wx, wy = G.window.get_size()
        status = (1 - self.parts[-1].get_status()) * len(self.world_data) * 20
        ay = wy + status - 150
        for i, (_, sprite, labels, _) in enumerate(self.world_data):
            sprite.x = 50
            sprite.y = ay
            dy = ay
            for label in labels:
                label.x = 120
                label.y = dy + 36
                dy -= 15
            ay -= 60

        if (wy - 140) / 60 > len(self.world_data):
            self.parts[-1].active = False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)
        elif symbol == key.R:  # "R" will reload the world list
            self.reload_world_icons()
        elif (
            symbol == key.ENTER and self.selected_world is not None
        ):  # selecting world & pressing enter will launch it
            self.enter_world(self.selected_world)
        elif (
            symbol == key.UP
            and self.selected_world is not None
            and self.selected_world > 0
        ):
            self.selected_world -= 1
            self.parts[-1].move(60)
        elif (
            symbol == key.DOWN
            and self.selected_world is not None
            and self.selected_world < len(self.world_data) - 1
        ):
            self.selected_world += 1
            self.parts[-1].move(-60)

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        x, y = G.window.mouse_position
        self.scissor_group.set_state()
        for i, (_, icon, labels, _) in enumerate(self.world_data):
            if icon.y < 105 or icon.y > wy - 110:
                continue
            icon.draw()
            for label in labels:
                label.draw()
            if i == self.selected_world:
                x, y = icon.position
                mcpython.util.opengl.draw_line_rectangle(
                    (x - 2, y - 2), (wx - 130, 54), (1, 1, 1)
                )
            px, py = icon.position
            if 0 <= x - px <= wx and 0 <= y - py <= 50:
                if 0 <= x - px <= 50:
                    self.selection_sprite.position = (
                        icon.position[0] + 25 - 16,
                        icon.position[1] + 25 - 16,
                    )
                    self.selection_sprite.draw()
        self.scissor_group.unset_state()
        mcpython.util.opengl.draw_line_rectangle(
            (45, 100), (wx - 90, wy - 160), (1, 1, 1)
        )

    def activate(self):
        super().activate()
        self.reload_world_icons()
        self.parts[-1].set_status(1)

    def reload_world_icons(self):
        if not os.path.exists(mcpython.server.storage.SaveFile.SAVE_DIRECTORY):
            os.makedirs(mcpython.server.storage.SaveFile.SAVE_DIRECTORY)
        wx, wy = G.window.get_size()
        self.world_data.clear()
        for directory in os.listdir(mcpython.server.storage.SaveFile.SAVE_DIRECTORY):
            path = os.path.join(
                mcpython.server.storage.SaveFile.SAVE_DIRECTORY, directory
            ).replace("\\", "/")
            if os.path.isdir(path) and os.path.isfile(path + "/level.json"):
                if os.path.isfile(path + "/icon.png"):
                    icon = pyglet.image.load(path + "/icon.png")
                else:
                    icon = MISSING_TEXTURE
                sprite = pyglet.sprite.Sprite(icon)
                with open(path + "/level.json") as f:
                    data = json.load(f)
                edit_date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(path + "/level.json")
                )
                diff = datetime.datetime.now() - edit_date
                if diff.days < 5:
                    edit = "{} days ago".format(diff.days)
                else:
                    edit = "on {}".format(edit_date.isoformat())
                labels = [
                    pyglet.text.Label(directory),
                    pyglet.text.Label(
                        "last played in version '{}' {}".format(
                            data["game version"], edit
                        )
                    ),
                    pyglet.text.Label(
                        "last loaded with {} mod{}".format(
                            len(data["mods"]), "" if len(data["mods"]) <= 1 else "s"
                        )
                    ),
                ]
                self.world_data.append((edit_date, sprite, labels, path))
        self.world_data.sort(key=lambda d: -d[0].timestamp())
        self.recalculate_sprite_position()
        if (wy - 140) / 60 > len(self.world_data):
            self.parts[-1].active = False

    def on_back_press(self, *_):
        G.state_handler.switch_to("minecraft:startmenu")

    def on_new_world_press(self, *_):
        G.state_handler.switch_to("minecraft:world_generation_config")

    def on_delete_press(self, *_):
        if self.selected_world is None:
            return
        shutil.rmtree(self.world_data[self.selected_world][3])
        self.reload_world_icons()

    def on_world_load_press(self, *_):
        if self.selected_world is None:
            return
        self.enter_world(self.selected_world)

    def enter_world(self, number: int):
        G.world.cleanup()
        G.world.setup_by_filename(self.world_data[number][2][0].text)
        G.state_handler.switch_to("minecraft:world_loading")


world_selection = None


@onlyInClient()
def create():
    global world_selection
    world_selection = StateWorldSelection()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
