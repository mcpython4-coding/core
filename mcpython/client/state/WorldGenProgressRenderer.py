from .AbstractStateRenderer import AbstractStateRenderer
from mcpython import shared
from mcpython.util.opengl import draw_rectangle


class WorldGenProgressRenderer(AbstractStateRenderer):
    def draw(self):
        wx, wy = shared.window.get_size()
        mx, my = wx // 2, wy // 2
        self.assigned_state.parts[1].text = "{}%".format(
            round(self.assigned_state.calculate_percentage_of_progress() * 1000) / 10
        )
        self.assigned_state.parts[2].text = "{}/{}/{}".format(
            *shared.world_generation_handler.task_handler.get_total_task_stats()
        )

        for cx, cz in self.assigned_state.status_table:
            status = self.assigned_state.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            elif status == -1:
                color = (0, 255, 0)
            else:
                color = (136, 0, 255)
            draw_rectangle(
                (mx + cx * 10, my + cz * 10), (10, 10), color
            )

