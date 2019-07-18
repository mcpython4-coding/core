"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
from state.ui import (UIPartImage)
import pyglet


class Inventory:
    def __init__(self):
        self.active = False
        self.bgsprite: pyglet.sprite.Sprite = None
        self.bganchor = "MM"
        self.windowanchor = "MM"
        self.positon = (0, 0)
        G.inventoryhandler.add(self)
        self.slots = self.create_slots()

    def create_slots(self) -> list:
        return []

    def _get_position(self):
        x, y = self.positon
        wx, wy = G.window.get_size()
        sx, sy = self.bgsprite.image.size if self.bgsprite else (0, 0)
        if self.bganchor[0] == "M":
            x -= sx // 2
        elif self.bganchor[0] == "R":
            x -= sx
        if self.bganchor[1] == "M":
            y -= sy // 2
        elif self.bganchor[1] == "U":
            y -= sy
        if self.windowanchor[0] == "M":
            x -= wx // 2
        elif self.windowanchor[0] == "R":
            x = wx - abs(x)
        if self.windowanchor[1] == "M":
            y -= wy // 2
        elif self.windowanchor[1] == "U":
            y = wy - abs(y)
        return x, y

    def activate(self):
        G.inventoryhandler.show(self)

    def deactivate(self):
        G.inventoryhandler.hide(self)

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def is_closable_by_escape(self) -> bool: return True

    def is_always_open(self) -> bool: return False

    def draw(self):
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            sx, sy = self.bgsprite.image.size
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in self.slots:
            slot.draw()
        self.on_draw_overlay()

    def on_draw_background(self):
        pass

    def on_draw_over_backgroundimage(self):
        pass

    def on_draw_overlay(self):
        pass

    def is_blocking_interactions(self) -> bool:
        return True

