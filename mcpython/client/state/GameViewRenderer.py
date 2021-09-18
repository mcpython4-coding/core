from .AbstractStateRenderer import AbstractStateRenderer
import pyglet

from mcpython import shared


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

