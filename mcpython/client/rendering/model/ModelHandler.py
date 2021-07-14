"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import gc
import json
import sys
import traceback

import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.client.rendering.model.BlockModel
import mcpython.client.rendering.model.BlockState
import mcpython.common.mod.ModMcpython
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import mcpython.util.math
from mcpython import shared
from mcpython.engine import logger


class ModelHandler:
    def __init__(self):
        self.models = {}
        self.used_models = set()
        self.found_models = {}
        self.blockstates = {}
        self.lookup_locations = set()
        self.dependence_list = []
        self.hide_blockstate_errors = False
        self.raw_models = []

    def add_from_mod(self, modname: str):
        """
        will add locations for an given mod name
        :param modname: the mod to use
        """
        self.lookup_locations.add("assets/{}/models/block".format(modname))

    def search(self):
        """
        Will search all locations for new stuff
        todo: add datapack locations
        """
        for location in self.lookup_locations:
            found_models = mcpython.engine.ResourceLoader.get_all_entries(location)
            for model in found_models:
                s = model.split("/")
                mod_fix = s[s.index("block") - 2]
                address_fix = "/".join(s[s.index("block") + 1 :])
                name = mod_fix + ":block/" + ".".join(address_fix.split(".")[:-1])
                self.found_models[name] = model

        for data, name in self.raw_models:
            if name not in self.models:
                self.found_models[name] = data

        shared.event_handler.call("modelhandler:searched")

    def add_from_data(self, name: str, data: dict, store=True):
        """
        will inject data as an block-model file
        :param name: the name to use
        :param data: the data to inject
        :param store: if it should be stored and re-loaded on reload event
        """
        self.found_models[name] = data
        if store:
            self.raw_models.append((data, name))

    def build(self, immediate=False):
        [
            self.let_subscribe_to_build(model, immediate=immediate)
            for model in self.used_models
        ]

    def let_subscribe_to_build(self, model, immediate=False):
        modname = model.split(":")[0] if model.count(":") == 1 else "minecraft"
        if modname not in shared.mod_loader.mods:
            modname = "minecraft"
        if immediate:
            self.special_build(model)
        else:
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:model:model_bake_prepare",
                self.special_build,
                model,
                info="filtering model '{}'".format(model),
            )

    def special_build(self, used: str):
        if used.count(":") == 0:
            used = "minecraft:" + used
        if used not in self.found_models:
            # logger.println("model error: can't locate model for '{}'".format(used))
            return
        file = self.found_models[used]
        if type(file) == str:
            try:
                data = mcpython.engine.ResourceLoader.read_json(file)
            except json.decoder.JSONDecodeError:
                data = {
                    "parent": "minecraft:block/cube_all",
                    "textures": {"all": "assets/missing_texture.png"},
                }
                logger.print_exception(
                    "during loading model from file {}, now replaced by missing texture".format(
                        file
                    )
                )
        else:
            data = file
        if "parent" in data:
            self.special_build(data["parent"])
            depend = [data["parent"]]
        else:
            depend = []
        self.dependence_list.append(
            (used, [e if ":" in e else "minecraft:" + e for e in depend])
        )

    def process_models(self, immediate=False):
        try:
            sorted_models = mcpython.util.math.topological_sort(self.dependence_list)
            if "minecraft:block/block" in sorted_models:
                sorted_models.remove("minecraft:block/block")
            if "block/block" in sorted_models:
                sorted_models.remove("block/block")
        except:
            logger.println(self.found_models, "\n", self.dependence_list)
            logger.print_exception("top-sort error during sorting models")
            import mcpython.client.state.StateLoadingException as StateLoadingException
            from mcpython.common.mod.ModLoader import LoadingInterruptException

            StateLoadingException.error_occur(traceback.format_exc())
            traceback.print_exc()

            raise LoadingInterruptException from None

        sorted_models = list(set(sorted_models))
        self.dependence_list.clear()  # decrease memory usage
        for x in sorted_models:
            modname = x.split(":")[0] if x.count(":") == 1 else "minecraft"
            if immediate:
                self.load_model(x)
            else:
                shared.mod_loader.mods[modname].eventbus.subscribe(
                    "stage:model:model_bake",
                    self.load_model,
                    x,
                    info="baking model '{}'".format(x),
                )

    def load_model(self, name: str):
        if ":" not in name:
            name = "minecraft:" + name
        if name in self.models:
            return
        location = self.found_models[name]
        try:
            if type(location) == str:
                modeldata = mcpython.engine.ResourceLoader.read_json(location)
                self.models[name] = mcpython.client.rendering.model.BlockModel.Model(
                    modeldata.copy(),
                    "block/" + location.split("/")[-1].split(".")[0],
                    name.split(":")[0] if name.count(":") == 1 else "minecraft",
                )
            else:
                self.models[name] = mcpython.client.rendering.model.BlockModel.Model(
                    location.copy(),
                    name,
                    name.split(":")[0] if name.count(":") == 1 else "minecraft",
                )
        except:
            logger.print_exception(
                "error during loading model '{}' named '{}'".format(location, name)
            )

    def add_face_to_batch(self, block, face, batches) -> list:
        if not shared.IS_CLIENT:
            return tuple()

        if block.NAME not in self.blockstates:
            if not self.hide_blockstate_errors:
                logger.println(
                    "[FATAL] block state for block '{}' not found!".format(block.NAME)
                )
            return self.blockstates["minecraft:missing_texture"].add_face_to_batch(
                block, batches, face
            )

        blockstate = self.blockstates[block.NAME]
        # todo: add custom block renderer check
        if blockstate is None:
            vertex = self.blockstates["minecraft:missing_texture"].add_face_to_batch(
                block, batches, face
            )
        else:
            vertex = blockstate.add_face_to_batch(block, batches, face)
            if issubclass(
                type(block.face_state.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBlockVertexManager,
            ):
                block.face_state.custom_renderer.handle(block, vertex)
        return vertex

    def add_raw_face_to_batch(
        self, position, state, block_state_name: str, batches, face
    ):
        if block_state_name is None or block_state_name not in self.blockstates:
            vertex = self.blockstates[
                "minecraft:missing_texture"
            ].add_raw_face_to_batch(position, state, batches, face)
        else:
            blockstate = self.blockstates[block_state_name]
            vertex = blockstate.add_raw_to_batch(position, state, batches, face)
        return vertex

    def draw_face(self, block, face):
        if not shared.IS_CLIENT:
            return

        if block.NAME not in self.blockstates:
            if not self.hide_blockstate_errors:
                logger.println(
                    "[FATAL] block state for block '{}' not found!".format(block.NAME)
                )
            return
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
        mcpython.client.rendering.model.BlockState.BlockStateDefinition.TO_CREATE.clear()
        mcpython.client.rendering.model.BlockState.BlockStateDefinition.NEEDED.clear()
        for (
            directory,
            modname,
        ) in (
            mcpython.client.rendering.model.BlockState.BlockStateDefinition.LOOKUP_DIRECTORIES
        ):
            mcpython.client.rendering.model.BlockState.BlockStateDefinition.from_directory(
                directory, modname, immediate=True
            )
        for (
            data,
            name,
            force,
        ) in mcpython.client.rendering.model.BlockState.BlockStateDefinition.RAW_DATA:
            mcpython.client.rendering.model.BlockState.BlockStateDefinition.unsafe_from_data(
                name, data, immediate=True, force=force
            )
        shared.event_handler.call("data:blockstates:custom_injection", self)
        shared.event_handler.call("data:models:custom_injection", self)
        self.build(immediate=True)
        self.process_models(immediate=True)
        logger.println("finished!")


shared.model_handler = ModelHandler()

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_search",
    shared.model_handler.add_from_mod,
    "minecraft",
    info="searching for block models for minecraft",
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_create", shared.model_handler.search, info="loading found models"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_bake_prepare",
    shared.model_handler.build,
    info="filtering models",
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_bake:prepare",
    shared.model_handler.process_models,
    info="preparing model data",
)
