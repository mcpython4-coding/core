"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import item.Item


class ItemHandler:
    def __init__(self):
        self.items = {}

    def register(self, itemclass: type(item.Item)):
        self(itemclass)

    def __call__(self, itemclass: type(item.Item), overwrite=True):
        if itemclass.get_name() in self.items and not overwrite: return
        self.items[itemclass.get_name()] = itemclass
        self.items[itemclass.get_name().split(":")[-1]] = itemclass


G.itemhandler = ItemHandler()

from . import (ItemStone)

