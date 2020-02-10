"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import ResourceLocator
import util.math
import rendering.model.Model
import traceback
import mod.ModMcpython
import logger


class ModelHandler:
    def __init__(self):
        self.models = {}
        self.used_models = []
        self.found_models = {}
        self.blockstates = {}
        self.lookup_locations = []
        self.dependence_list = []

    def add_from_mod(self, modname):
        self.lookup_locations.append("assets/{}/models/block".format(modname))

    def search(self):
        for location in self.lookup_locations:
            found_models = ResourceLocator.get_all_entries(location)
            for model in found_models:
                s = model.split("/")
                mod_fix = s[s.index("block")-2]
                address_fix = "/".join(s[s.index("block")+1:])
                name = ("" if mod_fix == "minecraft" else mod_fix+":") + "block/" + ".".join(
                    address_fix.split(".")[:-1])
                self.found_models[name] = model
        G.eventhandler.call("modelhandler:searched")

    def add_from_data(self, name, data):
        self.found_models[name] = data

    def build(self): [self.__let_subscribe_to_build(model) for model in self.used_models]

    def __let_subscribe_to_build(self, model):
        modname = model.split(":")[0] if model.count(":") == 1 else "minecraft"
        G.modloader.mods[modname].eventbus.subscribe("stage:model:model_bake_prepare", self.special_build, model,
                                                     info="filtering model {}".format(model))

    def special_build(self, used):
        if used not in self.found_models:
            logger.println("model error: can't locate model for {}".format(used))
            return
        file = self.found_models[used]
        if type(file) == str:
            data = ResourceLocator.read(file, "json")
        else:
            data = file
        if "parent" in data:
            self.__let_subscribe_to_build(data["parent"])
            depend = [data["parent"]]
        else:
            depend = []
        self.dependence_list.append((used, depend))

    def process_models(self):
        sorted_models = util.math.topological_sort(self.dependence_list)
        sorted_models = list(set(sorted_models))
        self.dependence_list = []  # decrease memory usage
        for x in sorted_models:
            modname = x.split(":")[0] if x.count(":") == 1 else "minecraft"
            G.modloader.mods[modname].eventbus.subscribe("stage:model:model_bake", self.load_model, x,
                                                         info="baking model {}".format(x))

    def load_model(self, name: str):
        if name in self.models: return
        location = self.found_models[name]
        try:
            if type(location) == str:
                modeldata = ResourceLocator.read(location, "json")
                self.models[name] = rendering.model.Model.Model(modeldata.copy(),
                                                              "block/" + location.split("/")[-1].split(".")[0])
            else:
                self.models[name] = rendering.model.Model.Model(location.copy(), name)
        except:
            logger.println("error during loading model {} named {}".format(location, name))
            traceback.print_exc()
            traceback.print_stack()

    def add_face_to_batch(self, block, face, batches) -> list:
        blockstate = self.get_block_state_for_block(block)
        # todo: add custom block renderer check
        if blockstate is None: return []  # todo: add missing texture
        return blockstate.add_face_to_batch(block, batches, face)

    def get_block_state_for_block(self, block):
        blockstatedefinition = self.blockstates[block.get_name()]
        blockstate = blockstatedefinition.get_state_for(block.get_model_state())
        if not blockstate: return None
        return blockstatedefinition.get_state_for(block.get_model_state())


G.modelhandler = ModelHandler()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_search", G.modelhandler.add_from_mod, "minecraft",
                                            info="searching for block models")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_create", G.modelhandler.search,
                                            info="loading found models")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_bake_prepare", G.modelhandler.build,
                                            info="filtering models")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_bake:prepare", G.modelhandler.process_models,
                                            info="preparing model data")

