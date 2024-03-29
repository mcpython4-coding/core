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
import asyncio
import gc
import json
import math
import traceback
import typing

import deprecation
import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.client.rendering.model.BlockModel
import mcpython.client.rendering.model.BlockState
import mcpython.common.mod.ModMcpython
import mcpython.engine.ResourceLoader
import mcpython.util.math
from bytecodemanipulation.Optimiser import (
    guarantee_builtin_names_are_protected,
    cache_global_name,
)
from mcpython import shared
from mcpython.client.rendering.model.api import IBlockStateRenderingTarget
from mcpython.client.rendering.model.BoxModel import ColoredRawBoxModel
from mcpython.client.texture.AnimationManager import animation_manager
from mcpython.engine import logger
from mcpython.util.enums import EnumSide


# @forced_attribute_type("models", lambda: dict)
# @forced_attribute_type("used_models", lambda: set)
# @forced_attribute_type("found_models", lambda: dict)
# @forced_attribute_type("blockstates", lambda: dict)
# @forced_attribute_type("lookup_locations", lambda: set)
# @forced_attribute_type("dependence_list", lambda: list)
# @forced_attribute_type("hide_blockstate_errors", lambda: bool)
# @forced_attribute_type("raw_models", list)
# @forced_attribute_type("break_stages", list)
class ModelHandler:
    def __init__(self):
        self.models: typing.Dict[str, typing.Any] = {}
        self.used_models: typing.Set[str] = set()
        self.found_models: typing.Dict[str, typing.Any] = {}
        self.blockstates: typing.Dict[str, typing.Any] = {}
        self.lookup_locations: typing.Set[str] = set()
        self.dependence_list = []
        self.hide_blockstate_errors = False
        self.raw_models = []

        SIZE = (1.002,) * 3

        # todo: reload these textures on normal reload
        self.break_stages = [
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_0.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_1.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_2.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_3.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_4.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_5.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_6.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_7.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_8.png",
            ),
            ColoredRawBoxModel(
                (0, 0, 0),
                SIZE,
                "assets/minecraft/textures/block/destroy_stage_9.png",
            ),
        ]

    async def add_from_mod(self, modname: str):
        """
        Will add locations for a given mod name
        :param modname: the mod to use
        """
        self.lookup_locations.add("assets/{}/models/block".format(modname))

    async def search(self):
        """
        Will search all locations for new stuff
        todo: add datapack locations
        """
        for location in self.lookup_locations:
            found_models = await mcpython.engine.ResourceLoader.get_all_entries(
                location
            )
            for model in found_models:
                s = model.split("/")
                mod_fix = s[s.index("block") - 2]
                address_fix = "/".join(s[s.index("block") + 1 :])
                name = mod_fix + ":block/" + ".".join(address_fix.split(".")[:-1])
                self.found_models[name] = model

        for data, name in self.raw_models:
            if name not in self.models:
                self.found_models[name] = data

        await shared.event_handler.call_async("minecraft:model_handler:searched")

    def add_from_data(self, name: str, data: dict, store=True):
        """
        Will inject data as a block-model file
        :param name: the name to use
        :param data: the data to inject
        :param store: if it should be stored and re-loaded on reload event
        """
        self.found_models[name] = data
        if store:
            self.raw_models.append((data, name))

    async def build(self, immediate=False):
        await asyncio.gather(
            *(
                self.let_subscribe_to_build(model, immediate=immediate)
                for model in self.used_models
            )
        )

    async def let_subscribe_to_build(self, model, immediate=False):
        modname = model.split(":")[0] if model.count(":") == 1 else "minecraft"

        if modname == "alias":
            return

        if modname not in shared.mod_loader.mods:
            logger.println(
                f"[MODEL MANAGER][WARN] namespace {modname} has no assigned mod; Using default mod for loading annotation"
            )
            modname = "minecraft"

        if immediate:
            await self.special_build(model)
        else:
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:model:model_bake_prepare",
                self.special_build(model),
                info="filtering model '{}'".format(model),
            )

    async def special_build(self, used: str):
        if used.count(":") == 0:
            used = "minecraft:" + used

        if used not in self.found_models:
            return

        file = self.found_models[used]

        if type(file) == str:
            try:
                data = await mcpython.engine.ResourceLoader.read_json(file)
            except json.decoder.JSONDecodeError:
                data = {
                    "parent": "minecraft:block/cube_all",
                    "textures": {"all": "assets/missing_texture.png"},
                }
                logger.println(
                    f"[WARN] json error during loading model from file {file}, now replaced by a missing texture block"
                )

        elif isinstance(file, dict):
            data = file

        else:
            raise ValueError(file)

        if "parent" in data:
            await self.special_build(data["parent"])
            depend = [data["parent"]]
        else:
            depend = []

        self.dependence_list.append(
            (used, [e if ":" in e else "minecraft:" + e for e in depend])
        )

    async def process_models(self, immediate=False):
        try:
            sorted_models = mcpython.util.math.topological_sort(self.dependence_list)

            if "minecraft:block/block" in sorted_models:
                sorted_models.remove("minecraft:block/block")

            if "block/block" in sorted_models:
                sorted_models.remove("block/block")

        except:
            logger.println(self.found_models, "\n", self.dependence_list)
            logger.print_exception("top-sort error during sorting models")

            import mcpython.common.state.LoadingExceptionViewState as StateLoadingException
            from mcpython.common.mod.util import LoadingInterruptException

            StateLoadingException.error_occur(traceback.format_exc())
            traceback.print_exc()

            raise LoadingInterruptException from None

        self.dependence_list.clear()  # decrease memory usage

        await asyncio.gather(
            *(
                self.load_model(x)
                for x in sorted_models
            )
        )

    async def load_model(self, name: str):
        if ":" not in name:
            name = "minecraft:" + name

        if name in self.models:
            return

        if name not in self.found_models:
            logger.println(
                f"[FATAL] model {name} was requested to be loaded, but never was required to be loaded"
            )
            return

        location = self.found_models[name]
        try:
            if type(location) == str:
                try:
                    model_data = await mcpython.engine.ResourceLoader.read_json(
                        location
                    )
                except json.decoder.JSONDecodeError:
                    logger.println(
                        "[WARN] invalid or corrupted .json file: " + location
                    )
                    self.models[name] = None
                else:
                    try:
                        self.models[
                            name
                        ] = await mcpython.client.rendering.model.BlockModel.Model(
                            "block/" + location.split("/")[-1].split(".")[0],
                            name.split(":")[0] if name.count(":") == 1 else "minecraft",
                        ).parse_from_data(
                            model_data.copy()
                        )

                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except:
                        logger.print_exception(f"during decoding model {location}")
                        self.models[name] = None

            else:
                try:
                    self.models[
                        name
                    ] = await mcpython.client.rendering.model.BlockModel.Model(
                        name,
                        name.split(":")[0] if name.count(":") == 1 else "minecraft",
                    ).parse_from_data(
                        location.copy()
                    )

                except (SystemExit, KeyboardInterrupt):
                    raise
                except:
                    logger.print_exception(f"during decoding model {name} [{location}]")
                    self.models[name] = None

        except (SystemExit, KeyboardInterrupt):
            raise
        except:
            logger.print_exception(
                "error during loading model '{}' named '{}'".format(location, name)
            )

    @deprecation.deprecated()
    def add_face_to_batch(
        self, block: IBlockStateRenderingTarget, face: EnumSide, batches
    ) -> typing.Iterable:
        if not shared.IS_CLIENT:
            return tuple()

        if block.NAME not in self.blockstates:
            return tuple()

        blockstate = self.blockstates[block.NAME]

        if blockstate is None:
            return tuple()

        return blockstate.add_face_to_batch(block, batches, face)

    def add_faces_to_batch(
        self, block, faces: int, batches: typing.List
    ) -> typing.Iterable:
        """
        Adds a collection of faces to a batch
        :param block: the thing to get rendering information from
        :param faces: n bitmap describing the faces
        :param batches: the batches to render into  todo: make single-atlas able
        :return: a list of vertex lists
        """
        if not shared.IS_CLIENT:
            return tuple()

        if block.NAME not in self.blockstates:
            if not self.hide_blockstate_errors:
                logger.println(
                    "[FATAL] block state for block '{}' not found!".format(block.NAME)
                )

            return tuple()

        blockstate = self.blockstates[block.NAME]

        if blockstate is None:
            return tuple()

        return blockstate.add_faces_to_batch(block, batches, faces)

    def add_raw_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position,
        state,
        block_state_name: str,
        batches,
        face,
    ):
        if block_state_name is None or block_state_name not in self.blockstates:
            vertex_list = self.blockstates[
                "minecraft:missing_texture"
            ].add_raw_face_to_batch(instance, position, state, batches, face)
        else:
            blockstate = self.blockstates[block_state_name]
            vertex_list = blockstate.add_raw_to_batch(
                instance, position, state, batches, face
            )

        return vertex_list

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

    def draw_face_scaled(self, block, face, scale: float):
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
        blockstate.draw_face_scaled(block, face, scale)

    def draw_block(self, block):
        [self.draw_face(block, face) for face in EnumSide.iterate()]

    def draw_block_scaled(self, block, scale: float):
        [self.draw_face_scaled(block, face, scale) for face in EnumSide.iterate()]

    def get_bbox(self, block):
        return self.blockstates[block.NAME].loader.transform_to_bounding_box(block)

    @cache_global_name("logger", lambda: logger)
    async def reload_models(self):
        logger.println("deleting content of models...")

        # clear the structures holding the data...
        self.models.clear()
        self.found_models.clear()
        self.dependence_list.clear()
        self.blockstates.clear()

        gc.collect()

        logger.println("loading models...")
        # and now start reloading models...
        await self.search()
        mcpython.client.rendering.model.BlockState.BlockStateContainer.TO_CREATE.clear()
        mcpython.client.rendering.model.BlockState.BlockStateContainer.NEEDED.clear()

        logger.println("walking across block states...")
        await asyncio.gather(
            *(
                mcpython.client.rendering.model.BlockState.BlockStateContainer.from_directory(
                    directory, modname, immediate=True
                )
                for (directory, modname,) in (
                    mcpython.client.rendering.model.BlockState.BlockStateContainer.LOOKUP_DIRECTORIES
                )
            )
        )

        logger.println("walking across located block states...")
        await asyncio.gather(
            *(
                mcpython.client.rendering.model.BlockState.BlockStateContainer.unsafe_from_data(
                    name, data, immediate=True, force=force
                )
                for name, data, force in mcpython.client.rendering.model.BlockState.BlockStateContainer.RAW_DATA
            )
        )

        await shared.event_handler.call_async(
            "minecraft:data:blockstates:custom_injection", self
        )

        logger.println("walking across requested models...")
        await self.build(immediate=True)
        await self.process_models(immediate=True)
        await animation_manager.bake()

        logger.println("finished!")

    def draw_block_break_overlay(
        self, position: typing.Tuple[float, float, float], progress: float
    ):
        stage = math.floor(progress * 10)

        if stage == 0:
            return

        model = self.break_stages[stage - 1]
        model.draw(position, color=(1, 1, 1, 0.7))


shared.model_handler = ModelHandler()

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_search",
    shared.model_handler.add_from_mod("minecraft"),
    info="searching for block models for minecraft",
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_create",
    shared.model_handler.search(),
    info="loading found models",
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_bake_prepare",
    shared.model_handler.build(),
    info="filtering models",
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:model_bake:prepare",
    shared.model_handler.process_models(),
    info="preparing model data",
)
