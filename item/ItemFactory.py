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
    EXTENSIONS = {}

    @classmethod
    def add_extension(cls, constructor, name):
        cls.EXTENSIONS[name] = constructor

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
            ItemFactory.load_from_data(data)
        ItemFactory.FILES = []

    @staticmethod
    def load_from_data(data):
        if type(data) == str:
            data = {"name": data, "image_file": "item/{}".format(data.split(":")[1])}
        if type(data) == dict and "mode" in data:
            ItemFactory.EXTENSIONS[data["mode"]](data)
        elif type(data) == list:
            [ItemFactory.load_from_data(d) for d in data]
        else:
            G.registry.register(ItemFactory.create_item_normal(data))

    @staticmethod
    def create_item_normal(data, base_class=item.Item.Item):
        class GeneratedItem(base_class):
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
            def get_default_item_image_location() -> str:
                return data["image_file"] if "image_file" in data else "item/"+data["name"].split(":")[1]

            @staticmethod
            def get_as_item_image(image: PIL.Image.Image) -> PIL.Image.Image: return image.resize(
                data["image_size"] if "image_size" in data else (32, 32)
            )

            def get_max_stack_size(self) -> int:
                return data["stacksize"] if "stacksize" in data else 64
        return GeneratedItem


def with_tag_construct(data):
    [ItemFactory.load_from_data(data["name"].format(x)) for x in G.taghandler.taggroups["naming"].
        tags[data["tagname"]].entries]


ItemFactory.add_extension(with_tag_construct, 'tagconstruct')


def with_multi_same_config(data):
    for entry in data["entries"]:
        if type(entry) == dict:
            ItemFactory.load_from_data({**data["config"], **entry})
        else:
            ItemFactory.load_from_data({"name": entry, **data["config"]})


ItemFactory.add_extension(with_multi_same_config, "mutlisameconfig")


def with_custom_listed(data):
    # an dict of entrielenght as str -> {<setted key>: <value>, <config key>: #<config entry id>}
    construct: dict = data["construct"]
    for entry in data["entries"]:
        data = construct[str(len(entry))].copy()
        for key in data.keys():
            if data[key].startswith("#"):
                data[key] = entry[int(data[key][1:])]
        ItemFactory.create_item_normal(data)


ItemFactory.add_extension(with_custom_listed, "custom_listed")

