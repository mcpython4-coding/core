"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import block.IBlock
import os
import json


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
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                file = os.path.join(root, name)
                if file not in BlockFactory.FILES:  # check for "is loaded"
                    BlockFactory.FILES.append(file)

    @staticmethod
    def load():
        """
        loads all block data from system
        """
        for file in BlockFactory.FILES:
            if file in BlockFactory.loaded:  # check if block was created
                continue
            BlockFactory.loaded.append(file)
            with open(file) as f:
                data = json.load(f)
            BlockFactory.create_block_normal(data.copy())

    @staticmethod
    def create_block_normal(data):
        """
        creates an block based on input data
        :param data: the data to use
        """

        @G.blockhandler
        class BlockFactoried(block.Block.Block if "injections" not in data else block.IBlock.InjectAbleBlock):
            """
            block class created by BlockFactory
            """
            # read injection classes
            INJECTION_CLASSES = data["injections"] if "injections" in data else []

            @staticmethod
            def get_name() -> str:
                return data["name"]

            def get_model_name(self):
                return data["model"] if "model" in data else super().get_model_name()

            def is_brakeable(self) -> bool:
                return data["brakeable"] if "brakeable" in data else super().is_brakeable()

