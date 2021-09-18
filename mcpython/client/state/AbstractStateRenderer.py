import typing
from abc import ABC

import pyglet


class AbstractStateRenderer(ABC):
    """
    Base class for state renderers
    """

    ASSIGNED_DRAW_STAGE = "render:draw:2d"

    def __init__(self):
        self.batch: typing.Optional[pyglet.graphics.Batch] = None
        self.assigned_state = None

    def init(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def draw(self):
        self.batch.draw()

    def resize(self, width: int, height: int):
        pass

