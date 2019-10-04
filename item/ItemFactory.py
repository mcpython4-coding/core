"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item
import os
import json
import PIL.Image
import ResourceLocator
import sys


class ItemFactory:
    FILES = []
    loaded = []

    @staticmethod
    def from_directory(directory):
        for file in ResourceLocator.get_all_entrys(directory):
            if file not in ItemFactory.FILES:
                ItemFactory.FILES.append(file)

    @staticmethod
    def load():
        if "--rebuild" not in sys.argv:
            ItemFactory.FILES.append(G.local + "/build/itemblockfactory.json")

        for file in ItemFactory.FILES:
            if file in ItemFactory.loaded:
                continue
            ItemFactory.loaded.append(file)
            data = ResourceLocator.read(file, "json")
            if type(data) == dict:
                if "mode" not in data:
                    ItemFactory.create_item_normal(data.copy())
                elif data["mode"] == "tagconstruct":
                    [ItemFactory.create_item_normal(data["name"].format(x)) for x in G.taghandler.taggroups["naming"].
                        tags[data["tagname"]].entries]
            elif type(data) == list:
                for entry in data:
                    ItemFactory.create_item_normal(entry.copy() if type(entry) == dict else entry)
        ItemFactory.FILES = []

    @staticmethod
    def create_item_normal(data):
        if type(data) == str:
            data = {"name": data, "image_file": "item/{}".format(data.split(":")[1])}

        @G.registry
        class GeneratedItem(item.Item.Item):
            @staticmethod
            def get_name() -> str:
                return data["name"]

            @staticmethod
            def has_block() -> bool:
                return data["has_block"] if "has_block" in data else False

            def get_block(self) -> str:
                return data["block"] if "block" in data else (self.get_name() if "has_block" in data and
                                                                                 data["has_block"] else None)

            @staticmethod
            def get_item_image_location() -> str:
                return data["image_file"] if "image_file" in data else "item/"+data["name"].split(":")[1]

            @staticmethod
            def get_as_item_image(image: PIL.Image.Image) -> PIL.Image.Image: return image.resize(
                data["image_size"] if "image_size" in data else (32, 32)
            )

            def get_max_stack_size(self) -> int:
                return data["stacksize"] if "stacksize" in data else 64

