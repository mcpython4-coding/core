"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import ResourceLocator
import random


class BlockStateDefinition:
    @staticmethod
    def from_directory(directory: str):
        for file in ResourceLocator.get_all_entrys(directory):
            if not file.endswith("/"):
                BlockStateDefinition.from_file(file)

    @staticmethod
    def from_file(file: str):
        try:
            return BlockStateDefinition(ResourceLocator.read(file, "json"), "minecraft:"+file.split("/")[-1].split(".")
                                        [0])
        except RuntimeError:
            return None

    def __init__(self, data: dict, name: str):
        G.modelhandler.blockstates[name] = self
        if name not in G.registry.get_by_name("block").get_attribute("blocks"): raise RuntimeError()
        self.states = []
        if "variants" in data:
            for element in data["variants"].keys():
                if element.count("=") > 0:
                    keymap = {}
                    for e in element.split(","):
                        keymap[e.split("=")[0]] = e.split("=")[1]
                else:
                    keymap = {}
                self.states.append((keymap, BlockState(data["variants"][element])))

    def get_state_for(self, data: dict):
        for keymap, blockstate in self.states:
            if keymap == data:
                return blockstate
        return None


class BlockState:
    def __init__(self, data):
        self.models = []  # (model, config)
        if type(data) == dict:
            if "model" in data:
                self.models.append(self._decode_entry(data))
                G.modelhandler.used_models.append(data["model"])
        elif type(data) == list:
            models = [self._decode_entry(x) for x in data]
            self.models += models
            G.modelhandler.used_models += [x[0] for x in models]

    @staticmethod
    def _decode_entry(data: dict):
        model = data["model"]
        G.modelhandler.used_models.append(model)
        rotations = (data["x"] if "x" in data else 0, data["y"] if "y" in data else 0,
                     data["z"] if "z" in data else 0)
        return model, {"rotation": rotations}

    def add_to_batch(self, position, batch):
        result = []
        model, config = random.choice(self.models)
        result += G.modelhandler.models[model].add_to_batch(position, batch, config)
        return result

