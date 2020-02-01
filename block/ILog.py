"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import block.Block
import event.TickHandler
import enum
from util.enums import LogAxis


class ILog(block.Block.Block):
    """
    base class for logs
    """

    def on_create(self):
        self.axis = LogAxis.Y
        if self.set_to:
            dx, dy, dz = abs(self.set_to[0] - self.position[0]), abs(self.set_to[1] - self.position[0]), \
                         abs(self.set_to[2] - self.position[2])
            if dx:
                self.axis = LogAxis.X
            elif dz:
                self.axis = LogAxis.Z

    def get_model_state(self): return {"axis": self.axis.name.lower()}

    def set_model_state(self, state: dict):
        if "axis" in state:
            axis: str = state["axis"]
            self.axis = LogAxis[axis.upper()]

    @staticmethod
    def get_all_model_states() -> list:
        return [{"axis": "x"}, {"axis": "y"}, {"axis": "z"}]

