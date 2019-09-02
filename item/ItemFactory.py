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


class ItemFactory:
    FILES = []
    loaded = []

    @staticmethod
    def from_directory(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                file = os.path.join(root, name)
                if file not in ItemFactory.FILES:
                    ItemFactory.FILES.append(file)

    @staticmethod
    def load():
        for file in ItemFactory.FILES:
            if file in ItemFactory.loaded:
                continue
            ItemFactory.loaded.append(file)
            with open(file) as f:
                data = json.load(f)
            ItemFactory.create_item_normal(data.copy())

    @staticmethod
    def create_item_normal(data):
        @G.itemhandler
        class GeneratedItem(item.Item.Item):
            @staticmethod
            def get_name() -> str:
                return data["name"]

            @staticmethod
            def has_block() -> bool:
                return data["has_block"] if "has_block" in data else False

            def get_block(self) -> str:
                return data["block"] if "block" in data else None

            @staticmethod
            def get_item_image_location() -> str:
                return data["image_file"]

            @staticmethod
            def get_as_item_image(image: PIL.Image.Image) -> PIL.Image.Image: return image.resize(
                data["image_size"] if "image_size" in data else (32, 32)
            )

            def get_max_stack_size(self) -> int:
                return data["stacksize"] if "stacksize" in data else 64

