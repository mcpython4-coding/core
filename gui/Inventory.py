"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from state.ui import (UIPartImage)
import pyglet
import ResourceLocator
import util.texture


class Inventory:
    """
    base inventory class
    """

    @staticmethod
    def get_config_file() -> str:
        """
        :return: the location of the inventory config file (if provided)
        """

    def __init__(self):
        self.active = False
        self.bgsprite: pyglet.sprite.Sprite = None
        self.bgimagesize = None
        self.bganchor = "MM"
        self.windowanchor = "MM"
        self.position = (0, 0)
        G.inventoryhandler.add(self)
        self.slots = self.create_slots()
        self.config = {}
        self.reload_config()
        self.on_create()

    def reload_config(self):
        """
        reload the config file
        """
        if self.get_config_file():
            self.config = ResourceLocator.read(self.get_config_file(), "json")
        else:
            self.config = {}
            return
        for slotid in self.config["slots"] if "slots" in self.config else []:
            sid = int(slotid)
            entry = self.config["slots"][slotid]
            if "position" in entry:
                # print(sid, entry)
                self.slots[sid].position = tuple(entry["position"])
            if "allow_player_insert" in entry:
                self.slots[sid].interaction_mode[1] = entry["allow_player_insert"]
            if "allow_player_remove" in entry:
                self.slots[sid].interaction_mode[0] = entry["allow_player_remove"]
            if "allow_player_add_to_free_place" in entry:
                self.slots[sid].interaction_mode[2] = entry["allow_player_add_to_free_place"]
            if "empty_slot_image" in entry:
                image = ResourceLocator.read(entry["empty_slot_image"], "pil")
                image = util.texture.to_pyglet_image(image.resize((32, 32)))
                self.slots[sid].empty_image = pyglet.sprite.Sprite(image)
        if "image_size" in self.config:
            self.bgimagesize = tuple(self.config["image_size"])
        if "image_anchor" in self.config:
            self.bganchor = self.config["image_anchor"]
        if "window_anchor" in self.config:
            self.windowanchor = self.config["window_anchor"]
        if "image_position" in self.config:
            self.position = self.config["image_position"]
        if "image_location" in self.config:
            self.bgsprite = pyglet.sprite.Sprite(ResourceLocator.read(self.config["image_location"], "pyglet"))
        self.on_create()

    def on_create(self):
        """
        callen when the inventory is created
        """

    def create_slots(self) -> list:
        """
        creates the slots
        :return: the slots the inventory uses
        """
        return []

    def _get_position(self):
        """
        :return: the position of the inventory
        """
        x, y = self.position
        wx, wy = G.window.get_size()
        sx, sy = self.bgimagesize if self.bgsprite else (0, 0)
        if self.bganchor[0] == "M":
            x -= sx // 2
        elif self.bganchor[0] == "R":
            x -= sx
        if self.bganchor[1] == "M":
            y -= sy // 2
        elif self.bganchor[1] == "U":
            y -= sy
        if self.windowanchor[0] == "M":
            x += wx // 2
        elif self.windowanchor[0] == "R":
            x = wx - abs(x)
        if self.windowanchor[1] == "M":
            y += wy // 2
        elif self.windowanchor[1] == "U":
            y = wy - abs(y)
        return x, y

    def activate(self):
        G.inventoryhandler.show(self)

    def deactivate(self):
        G.inventoryhandler.hide(self)

    def on_activate(self):
        """
        callen when the inventory is shown
        """

    def on_deactivate(self):
        """
        callen when the inventory is hidden
        """

    def is_closable_by_escape(self) -> bool: return True

    def is_always_open(self) -> bool: return False

    def draw(self, hoveringslot=None):
        """
        draws the inventory
        """
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in self.slots:
            slot.draw_lable()
        self.on_draw_overlay()

    def on_draw_background(self):
        """
        draw the background
        """

    def on_draw_over_backgroundimage(self):
        """
        draw between background and slots
        """

    def on_draw_over_image(self):
        """
        draw between slots and counts
        """

    def on_draw_overlay(self):
        """
        draw over anything else
        """

    def is_blocking_interactions(self) -> bool:
        return True

    def on_world_cleared(self):
        [slot.itemstack.clean() for slot in self.slots]
        if self in G.inventoryhandler.opened_inventorystack: G.inventoryhandler.hide(self)

    def get_interaction_slots(self):
        return self.slots

