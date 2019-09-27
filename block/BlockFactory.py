"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import block.IBlock
import os
import json
import ResourceLocator
import tags.TagHandler


class BlockFactory:
    """
    factory for creating blocks during runtime
    """

    FILES = []
    loaded = []

    @staticmethod
    def from_directory(directory):
        """
        generates blocks out of the .json files of the directory
        :param directory: the directory to search for
        """
        BlockFactory.FILES += ResourceLocator.get_all_entrys(directory)

    @staticmethod
    def load():
        """
        loads all block data from system
        """
        for file in BlockFactory.FILES:
            if file in BlockFactory.loaded:  # check if block was created
                continue
            BlockFactory.loaded.append(file)
            data = ResourceLocator.read(file, "json")
            if type(data) == dict:
                if "mode" not in data:
                    BlockFactory.create_block_normal(data.copy())
                elif data["mode"] == "multisameconfig":
                    for name in data["names"]:
                        config = data["config"].copy()
                        config["name"] = name
                        BlockFactory.create_block_normal(config)
                elif data["mode"] == "colornamed":
                    BlockFactory.create_block_normal_from_array([data["name"].format(color) for color in
                                                                 G.taghandler.taggroups["naming"].tags[
                                                                     "#minecraft:colors"].entries])
                elif data["mode"] == "multisameconfig_colornamed":
                    for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
                        config = data["config"].copy()
                        config["name"] = data["name"].format(color)
                        BlockFactory.create_block_normal(config)
            elif type(data) == list:
                BlockFactory.create_block_normal_from_array(data.copy())

    @classmethod
    def create_block_normal_from_array(cls, data: list):
        for entry in data:
            if type(entry) == str:
                cls.create_block_normal({"name": entry})
            elif type(entry) == dict:
                cls.create_block_normal(entry)

    @staticmethod
    def create_block_normal(data: dict):
        """
        creates an block based on input data
        :param data: the data to use
        """

        @G.registry
        class BlockFactoried(block.Block.Block if "injections" not in data else block.IBlock.InjectAbleBlock):
            """
            block class created by BlockFactory
            """
            # read injection classes
            INJECTION_CLASSES = data["injections"] if "injections" in data else []
            # print(INJECTION_CLASSES, data["name"])

            @staticmethod
            def get_name() -> str:
                return data["name"]

            def is_brakeable(self) -> bool:
                return data["brakeable"] if "brakeable" in data else super().is_brakeable()

            def get_model_state(self) -> dict: return {} if "modelstate" not in data else data["modelstate"]

            def is_solid_side(self, side) -> bool: return True if "solid" not in data else data["solid"]

