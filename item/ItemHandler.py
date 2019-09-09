"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item
import util.texture
import ResourceLocator
import event.Registry


def register_item(registry, itemclass):
    itemtable = registry.get_attribute("items")
    pygletimagetable = registry.get_attribute("pygletimagetable")
    itemtable[itemclass.get_name()] = itemclass
    itemtable[itemclass.get_name().split(":")[-1]] = itemclass
    pygletimagetable[itemclass.get_name()] = util.texture.to_pyglet_image(
        itemclass.get_as_item_image(ResourceLocator.read(itemclass.get_item_image_location(), "pil")))


items = event.Registry.Registry("item", [item.Item.Item], injection_function=register_item)
items.set_attribute("items", {})
items.set_attribute("pygletimagetable", {})

from . import (ItemFactory)

ItemFactory.ItemFactory.from_directory(G.local+"/assets/factory/item")

ItemFactory.ItemFactory.load()

