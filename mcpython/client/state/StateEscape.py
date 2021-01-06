"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLabel
import mcpython.common.event.EventInfo
from mcpython import shared as G
from pyglet.window import key
import pyglet
import mcpython.client.state.StateGame
import mcpython.util.callbacks
import mcpython.common.mod.ModMcpython
import time
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateEscape(State.State):
    NAME = "minecraft:escape_state"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [
            StatePartGame.StatePartGame(
                activate_keyboard=False,
                activate_mouse=False,
                activate_focused_block=False,
                glcolor3d=(0.8, 0.8, 0.8),
            ),
            UIPartLabel.UIPartLabel(
                "#*menu.game*#",
                (0, 200),
                anchor_lable="MM",
                anchor_window="MM",
                color=(255, 255, 255, 255),
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.returnToGame*#",
                (0, 150),
                anchor_window="MM",
                anchor_button="MM",
                on_press=mcpython.common.event.EventInfo.CallbackHelper(
                    G.state_handler.switch_to,
                    ["minecraft:game"],
                    enable_extra_args=False,
                ),
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.returnToMenu*#",
                (0, 120),
                anchor_window="MM",
                anchor_button="MM",
                on_press=self.start_menu_press,
            ),
            UIPartButton.UIPartButton(
                (250, 25),
                "#*menu.reportBugs*#",
                (0, 90),
                anchor_window="MM",
                anchor_button="MM",
                on_press=mcpython.common.event.EventInfo.CallbackHelper(
                    mcpython.util.callbacks.open_github_project, enable_extra_args=False
                ),
            ),
            mcpython.client.state.StateGame.game.parts[1],
        ]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    @staticmethod
    def start_menu_press(x, y):
        G.world.world_loaded = False
        while G.world.save_file.save_in_progress:
            time.sleep(0.2)
        G.world.save_file.save_world(
            override=True
        )  # make sure that file size is as small as possible
        G.world.setup_by_filename("tmp")
        G.world.cleanup()
        G.event_handler.call("on_game_leave")
        G.state_handler.switch_to("minecraft:startmenu", immediate=False)
        while G.world.save_file.save_in_progress:
            time.sleep(0.2)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            G.state_handler.switch_to("minecraft:game", immediate=False)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)

    def activate(self):
        super().activate()
        pyglet.clock.schedule_once(G.world.save_file.save_world, 0.1)


escape = None


@onlyInClient()
def create():
    global escape
    escape = StateEscape()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
