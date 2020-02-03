"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import ResourceLocator
import random
import mod.ModMcpython
import traceback
import logger


class BlockStateNotNeeded(Exception): pass


class BlockStateDefinition:
    TO_CREATE = set()

    @staticmethod
    def from_directory(directory: str, modname: str):
        for file in ResourceLocator.get_all_entries(directory):
            if not file.endswith("/"):
                BlockStateDefinition.from_file(file, modname)

    @classmethod
    def from_file(cls, file: str, modname: str):
        G.modloader.mods[modname].eventbus.subscribe("stage:model:blockstate_create", cls._from_file, file,
                                                     info="loading block state {}".format(file))
        cls.TO_CREATE.add(file)

    @classmethod
    def _from_file(cls, file: str):
        try:
            s = file.split("/")
            modname = s[s.index("blockstates")-1]
            return BlockStateDefinition(ResourceLocator.read(file, "json"), "{}:{}".format(
                modname, s[-1].split(".")[0]))
        except BlockStateNotNeeded: pass
        except:
            logger.println("error during loading model from file {}".format(file))
            traceback.print_exc()

    @classmethod
    def from_data(cls, name, data):
        mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:blockstate_create", cls._from_data, name, data,
                                                    info="loading block state {}".format(name))

    @classmethod
    def _from_data(cls, name, data):
        try:
            return BlockStateDefinition(data, name)
        except BlockStateNotNeeded: pass  # do we need this model?
        except:
            logger.println("error during loading model for {} from data {}".format(name, data))
            traceback.print_exc()

    def __init__(self, data: dict, name: str):
        if name not in G.registry.get_by_name("block").get_attribute("blocks"): raise BlockStateNotNeeded()
        G.modelhandler.blockstates[name] = self
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

    def add_face_to_batch(self, block, batch, face):
        # todo: add some more functionality to this
        if block.block_state is None:
            block.block_state = random.randint(1, len(self.models)) - 1
        result = []
        model, config = self.models[block.block_state]
        if model not in G.modelhandler.models:
            raise ValueError("can't find model named '{}' to add at {}".format(model, block.position))
        result += G.modelhandler.models[model].add_face_to_batch(block.position, batch, config, face)
        return result


mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:blockstate_search", BlockStateDefinition.from_directory,
                                            "assets/minecraft/blockstates", "minecraft",
                                            info="searching for block states")
