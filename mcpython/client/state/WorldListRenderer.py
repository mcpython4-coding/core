from .AbstractStateRenderer import AbstractStateRenderer
from mcpython import shared
import pyglet
from mcpython.util.opengl import draw_line_rectangle


class WorldListRenderer(AbstractStateRenderer):
    def draw(self):
        wx, wy = shared.window.get_size()
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        x, y = shared.window.mouse_position
        self.assigned_state.scissor_group.set_state()
        for i, (_, icon, labels, _) in enumerate(self.assigned_state.world_data):
            icon.draw()
            for label in labels:
                label.draw()
            if i == self.assigned_state.selected_world:
                x, y = icon.position
                draw_line_rectangle(
                    (x - 2, y - 2), (wx - 130, 54), (1, 1, 1)
                )
            px, py = icon.position
            if 0 <= x - px <= wx and 0 <= y - py <= 50:
                if 0 <= x - px <= 50:
                    self.assigned_state.selection_sprite.position = (
                        icon.position[0] + 25 - 16,
                        icon.position[1] + 25 - 16,
                    )
                    self.assigned_state.selection_sprite.draw()
        self.assigned_state.scissor_group.unset_state()
        draw_line_rectangle(
            (45, 100), (wx - 90, wy - 160), (1, 1, 1)
        )

