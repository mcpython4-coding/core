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
import functools
import time

import mcpython.client.gui.ContainerRenderingManager
import mcpython.common.mod.ModMcpython
import mcpython.engine.event.EventInfo
import mcpython.util.callbacks
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient
from pyglet.window import key

from . import AbstractState, GameViewStatePart
from .ui import UIPartButton, UIPartLabel


@onlyInClient()
class EscapeMenu(AbstractState.AbstractState):
    NAME = "minecraft:escape_menu"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)

    def get_parts(self) -> list:
        return [
            GameViewStatePart.GameView(
                activate_keyboard=False,
                activate_mouse=False,
                activate_focused_block=False,
                gl_color_3d=(0.8, 0.8, 0.8),
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
                on_press=lambda *_: shared.state_handler.change_state(
                    "minecraft:game", immediate=False
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
                on_press=functools.partial(mcpython.util.callbacks.open_github_project),
            ),
            mcpython.client.gui.ContainerRenderingManager.inventory_part,
        ]

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    @staticmethod
    def start_menu_press(x, y):
        shared.world.world_loaded = False
        while shared.world.save_file.save_in_progress:
            time.sleep(0.2)

        if shared.IS_NETWORKING:
            shared.NETWORK_MANAGER.disconnect()

        # make sure that file size is as small as possible
        shared.world.save_file.save_world(override=True)

        shared.world.setup_by_filename("tmp")
        shared.world.cleanup()
        shared.event_handler.call("on_game_leave")
        shared.state_handler.change_state("minecraft:start_menu", immediate=False)

        while shared.world.save_file.save_in_progress:
            time.sleep(0.2)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            shared.state_handler.change_state("minecraft:game", immediate=False)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)

    def activate(self):
        super().activate()
        pyglet.clock.schedule_once(shared.world.save_file.save_world, 0.1)


escape = None


@onlyInClient()
def create():
    global escape
    escape = EscapeMenu()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
