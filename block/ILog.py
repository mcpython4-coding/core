"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import event.TickHandler
import enum


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


AXIS_MAP = {LogAxis.X: "x", LogAxis.Y: "y", LogAxis.Z: "z"}


class ILog(block.Block.Block):
    """
    base class for logs
    """

    def on_create(self):
        self.axis = LogAxis.Y
        if self.setted_to:
            dx, dy, dz = abs(self.setted_to[0] - self.position[0]), abs(self.setted_to[1] - self.position[0]), \
                            abs(self.setted_to[2] - self.position[2])
            if dx:
                self.axis = LogAxis.X
            elif dz:
                self.axis = LogAxis.Z

    def get_model_state(self):
        return {"axis": AXIS_MAP[self.axis]}

