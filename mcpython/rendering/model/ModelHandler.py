"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import gc
import sys

from mcpython import globals as G, logger
import mcpython.mod.ModMcpython
import mcpython.rendering.model.Model
import mcpython.rendering.model.BlockState
import mcpython.ResourceLocator
import mcpython.util.enums
import mcpython.util.math
import json
import mcpython.rendering.ICustomBlockRenderer


class ModelHandler:
    def __init__(self):
        self.models = {}
        self.used_models = []  # todo: change to set
        self.found_models = {}  # todo: clear when not needed
        self.blockstates = {}
        self.lookup_locations = []  # todo: change to set
        self.dependence_list = []  # todo: clear when not needed

    def add_from_mod(self, modname: str):
        """
        will add locations for an given mod name
        :param modname: the mod to use
        """
        self.lookup_locations.append("assets/{}/models/block".format(modname))

    def search(self):
        """
        will search all locations for new stuff
        todo: add datapack locations
        """
        for location in self.lookup_locations:
            found_models = mcpython.ResourceLocator.get_all_entries(location)
            for model in found_models:
                s = model.split("/")
                mod_fix = s[s.index("block") - 2]
                address_fix = "/".join(s[s.index("block") + 1:])
                name = mod_fix + ":block/" + ".".join(address_fix.split(".")[:-1])
                self.found_models[name] = model
        G.eventhandler.call("modelhandler:searched")

    def add_from_data(self, name: str, data: dict):
        """
        will inject data as an block-model file
        :param name: the name to use
        :param data: the data to inject
        """
        self.found_models[name] = data

    def build(self, immediate=False):
        [self.let_subscribe_to_build(model, immediate=immediate) for model in self.used_models]  # todo: use set intersection

    def let_subscribe_to_build(self, model, immediate=False):
        modname = model.split(":")[0] if model.count(":") == 1 else "minecraft"
        if modname not in G.modloader.mods: modname = "minecraft"
        if immediate:
            self.special_build(model)
        else:
            G.modloader.mods[modname].eventbus.subscribe("stage:model:model_bake_prepare", self.special_build, model,
                                                         info="filtering model '{}'".format(model))

    def special_build(self, used: str):
        if used.count(":") == 0:
            logger.println("[WARN] deprecated access to model without minecraft-prefix to '{}'".format(used))
            used = "minecraft:" + used
        if used not in self.found_models:
            # logger.println("model error: can't locate model for '{}'".format(used))
            return
        file = self.found_models[used]
        if type(file) == str:
            try:
                data = mcpython.ResourceLocator.read(file, "json")
            except json.decoder.JSONDecodeError:
                data = {"parent": "minecraft:block/cube_all", "textures": {"all": "assets/missingtexture.png"}}
                logger.write_exception("during loading model from file {}, now replaced by missing texture".format(file))
        else:
            data = file
        if "parent" in data:
            self.special_build(data["parent"])
            depend = [data["parent"]]
        else:
            depend = []
        self.dependence_list.append((used, [e if ":" in e else "minecraft:" + e for e in depend]))

    def process_models(self, immediate=False):
        try:
            sorted_models = mcpython.util.math.topological_sort(self.dependence_list)
            sorted_models.remove("minecraft:block/block")  # This is the build-in model and we don't need it
        except ValueError:
            logger.println(self.found_models, "\n", self.dependence_list)
            logger.write_exception("top-sort error during sorting models")
            sys.exit(-1)
        sorted_models = list(set(sorted_models))
        self.dependence_list.clear()  # decrease memory usage
        for x in sorted_models:
            modname = x.split(":")[0] if x.count(":") == 1 else "minecraft"
            if immediate:
                self.load_model(x)
            else:
                G.modloader.mods[modname].eventbus.subscribe("stage:model:model_bake", self.load_model, x,
                                                             info="baking model '{}'".format(x))

    def load_model(self, name: str):
        if ":" not in name: name = "minecraft:" + name
        if name in self.models: return
        location = self.found_models[name]
        try:
            if type(location) == str:
                modeldata = mcpython.ResourceLocator.read(location, "json")
                self.models[name] = mcpython.rendering.model.Model.Model(modeldata.copy(),
                                                                         "block/" + location.split("/")[-1].split(".")[
                                                                             0],
                                                                         name.split(":")[0] if name.count(":") == 1 else
                                                                         "minecraft")
            else:
                self.models[name] = mcpython.rendering.model.Model.Model(location.copy(), name,
                                                                         name.split(":")[0] if name.count(":") == 1 else
                                                                         "minecraft")
        except:
            logger.write_exception("error during loading model '{}' named '{}'".format(location, name))

    def add_face_to_batch(self, block, face, batches) -> list:
        if block.NAME not in self.blockstates:
            logger.println("[FATAL] block state for block '{}' not found!".format(block.NAME))
            logger.println("possible:", self.blockstates.keys())
            return []
        blockstate = self.blockstates[block.NAME]
        # todo: add custom block renderer check
        if blockstate is None:
            vertex = self.blockstates["minecraft:missing_texture"].add_face_to_batch(block, batches, face)
        else:
            vertex = blockstate.add_face_to_batch(block, batches, face)
            if issubclass(type(block.face_state.custom_renderer), mcpython.rendering.ICustomBlockRenderer.ICustomBlockVertexManager):
                block.face_state.custom_renderer.handle(block, vertex)
        return vertex

    def draw_face(self, block, face):
        if block.NAME not in self.blockstates:
            # todo: add option to disable these prints
            logger.println("[FATAL] block state for block '{}' not found!".format(block.NAME))
            logger.println("possible:", self.blockstates.keys())
            return []
        blockstate = self.blockstates[block.NAME]
        # todo: add custom block renderer check
        if blockstate is None:
            self.blockstates["minecraft:missing_texture"].draw_face(block, face)
        blockstate.draw_face(block, face)

    def draw_block(self, block):
        [self.draw_face(block, face) for face in mcpython.util.enums.EnumSide.iterate()]

    def get_bbox(self, block):
        return self.blockstates[block.NAME].loader.transform_to_hitbox(block)

    def reload_models(self):
        logger.println("deleting content of models...")
        # clear the list holding the data...
        self.models.clear()
        self.found_models.clear()
        self.dependence_list.clear()
        self.blockstates.clear()
        gc.collect()  # ... and now delete the content

        logger.println("loading models...")
        # and now start reloading models...
        self.search()
        mcpython.rendering.model.BlockState.BlockStateDefinition.TO_CREATE.clear()
        mcpython.rendering.model.BlockState.BlockStateDefinition.NEEDED.clear()
        for directory, modname in mcpython.rendering.model.BlockState.BlockStateDefinition.LOOKUP_DIRECTORIES:
            mcpython.rendering.model.BlockState.BlockStateDefinition.from_directory(directory, modname, immediate=True)
        G.eventhandler.call("data:blockstates:custom_injection", self)
        G.eventhandler.call("data:models:custom_injection", self)
        self.build(immediate=True)
        self.process_models(immediate=True)
        logger.println("finished!")


G.modelhandler = ModelHandler()

mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_search", G.modelhandler.add_from_mod,
                                                     "minecraft",
                                                     info="searching for block models for minecraft")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_create", G.modelhandler.search,
                                                     info="loading found models")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_bake_prepare", G.modelhandler.build,
                                                     info="filtering models")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:model_bake:prepare", G.modelhandler.process_models,
                                                     info="preparing model data")
