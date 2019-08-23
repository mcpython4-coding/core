"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import block.IBlock
import os
import json
import traceback


class BlockFactory:
    FILES = []
    loaded = []

    @staticmethod
    def from_directory(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                file = os.path.join(root, name)
                if file not in BlockFactory.FILES:
                    BlockFactory.FILES.append(file)

    @staticmethod
    def load():
        for file in BlockFactory.FILES:
            if file in BlockFactory.loaded:
                continue
            BlockFactory.loaded.append(file)
            with open(file) as f:
                data = json.load(f)
            BlockFactory.create_block_normal(data.copy())

    @staticmethod
    def create_block_normal(data):

        @G.blockhandler
        class BlockFactoried(block.Block.Block if "injections" not in data else block.IBlock.InjectAbleBlock):
            INJECTION_CLASSES = data["injections"] if "injections" in data else []

            @staticmethod
            def get_name() -> str:
                return data["name"]

            def get_model_name(self):
                return data["model"]

            def is_brakeable(self) -> bool:
                return data["brakeable"] if "brakeable" in data else True

