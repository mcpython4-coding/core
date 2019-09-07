"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import ResourceLocator
import util.math
import texture.model.Model
import texture.TextureAtlas
import traceback


class ModelHandler:
    def __init__(self):
        self.models = {}
        self.used_models = []
        self.found_models = {}
        self.blockstates = {}

    def search(self):
        found_models = ResourceLocator.get_all_entrys("assets/minecraft/models/block")
        for model in found_models:
            self.found_models["block/"+model.split("/")[-1].split(".")[0]] = model

    def build(self):
        used_models = self.used_models[:]
        dependencied_list = []
        while len(used_models) > 0:
            used = used_models.pop(0)
            if used not in self.found_models:
                print("model error: can't locate model for {}".format(used))
            data = ResourceLocator.read(self.found_models[used], "json")
            if "parent" in data:
                used_models.append(data["parent"])
                depend = [data["parent"]]
            else:
                depend = []
            dependencied_list.append((used, depend))
        sorted_models = util.math.topological_sort(dependencied_list)
        sorted_models = list(set(sorted_models))
        for x in sorted_models:
            self.load_model(x)

    def load_model(self, name: str):
        if name in self.models: return
        location = self.found_models[name]
        try:
            modeldata = ResourceLocator.read(location, "json")
            self.models[name] = texture.model.Model.Model(modeldata.copy(),
                                                          "block/"+location.split("/")[-1].split(".")[0])
        except:
            print("error during loading model {} named {}".format(location, name))
            traceback.print_exc()
            traceback.print_stack()

    def add_to_batch(self, block, position, batch):
        blockstatedefinition = self.blockstates[block.get_name()]
        blockstate = blockstatedefinition.get_state_for(block.get_model_state())

        try:
            return blockstate.add_to_batch(position, batch)
        except:
            print(blockstatedefinition.states, block.get_name(), block.get_model_state())
            raise


G.modelhandler = ModelHandler()

