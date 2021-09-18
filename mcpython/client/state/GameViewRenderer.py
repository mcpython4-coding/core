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
import pyglet
from mcpython import shared

from .AbstractStateRenderer import AbstractStateRenderer


class GameViewRenderer(AbstractStateRenderer):
    ASSIGNED_DRAW_STAGE = "render:draw:2d:background"

    def init(self):
        self.assigned_state.eventbus.subscribe("render:draw:3d", self.draw_3d)

    def draw(self):
        if self.assigned_state.active_label:
            shared.window.draw_label()

        if self.assigned_state.activate_crosshair:
            shared.window.draw_reticle()

    def draw_3d(self):
        pyglet.gl.glClearColor(*self.assigned_state.clear_color)
        pyglet.gl.glColor3d(*self.assigned_state.color_3d)

        if self.assigned_state.activate_3d_draw:
            shared.world.get_active_dimension().draw()
            if (
                self.assigned_state.activate_focused_block_draw
                and shared.world.get_active_player().gamemode != 3
            ):
                # todo: move this method to player
                shared.window.draw_focused_block()
