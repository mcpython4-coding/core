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
import copy
import random
import typing

import deprecation
import mcpython.client.rendering.model.api
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
import mcpython.engine.physics.AxisAlignedBoundingBox
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import pyglet
from bytecodemanipulation.OptimiserAnnotations import (
    builtins_are_static,
    forced_arg_type,
    inline_call,
    try_optimise,
)
from mcpython import shared
from mcpython.client.rendering.model.api import (
    BlockStateNotNeeded,
    IBlockStateDecoder,
    IBlockStateRenderingTarget,
)
from mcpython.client.rendering.model.BoxModel import MutableRawBoxModel
from mcpython.client.rendering.model.util import decode_entry, get_model_choice
from mcpython.engine import logger
from mcpython.util.enums import EnumSide

blockstate_decoder_registry = mcpython.common.event.Registry.Registry(
    "minecraft:blockstates",
    ["minecraft:blockstate"],
    "stage:blockstate:register_loaders",
    sync_via_network=False,
)


class MultiPartDecoder(IBlockStateDecoder):
    """
    Decoder for mc multipart state files.
    WARNING: the following decoder has some extended features:
    entry parent: An parent DefaultDecoded blockstate from which states and model aliases should be copied
    entry alias: An dict of original -> aliased model to transform any model name of this kind in the system with the given model. Alias names MUST start with alias:

    todo: can we optimize it by pre-doing some stuff?
    todo: fix alias system
    """

    __slots__ = IBlockStateDecoder.__slots__ + ("parent", "model_alias")

    NAME = "minecraft:multipart_blockstate_loader"

    @classmethod
    @forced_arg_type("data", lambda: dict, may_subclass=False)
    def is_valid(cls, data: dict) -> bool:
        return (
            "multipart" in data
            and "forge_marker" not in data
            and "mod_marker" not in data
        )

    def __init__(self, block_state):
        super().__init__(block_state)
        self.parent = None
        self.model_alias = None

    @builtins_are_static()
    @forced_arg_type("data", lambda: dict, may_subclass=False)
    def parse_data(self, data: dict):
        self.data = data

        for entry in data["multipart"]:
            if type(entry["apply"]) == dict:
                shared.model_handler.used_models.add(entry["apply"]["model"])
            else:
                for d in entry["apply"]:
                    shared.model_handler.used_models.add(d["model"])

        self.model_alias: typing.Dict[str, typing.Any] = {}
        self.parent: typing.Union[str, "BlockStateContainer", None] = None

        if "parent" in data:
            self.parent = data["parent"]
            BlockStateContainer.NEEDED.add(self.parent)

        if "alias" in data:
            self.model_alias = data["alias"]

    async def bake(self):
        if self.parent is not None and isinstance(self.parent, str):
            try:
                parent: BlockStateContainer = await BlockStateContainer.get_or_load(
                    self.parent
                )
            except FileNotFoundError:
                self.parent = None
            else:
                if parent is None:
                    self.parent = None
                    return

                if not parent.baked:
                    return False

                if not issubclass(type(parent.loader), type(self)):
                    raise ValueError(
                        "parent must be subclass of the current loader ({} is not a subclass of {})".format(
                            type(self), type(parent.loader)
                        )
                    )

                self.parent = parent
                self.model_alias = {
                    **self.parent.loader.model_alias.copy(),
                    **self.model_alias,
                }
                self.data["multipart"].extend(
                    copy.deepcopy(self.parent.loader.data["multipart"])
                )

        for model in self.model_alias.values():
            shared.model_handler.used_models.add(model)

        for entry in self.data["multipart"]:
            data = entry["apply"]
            if type(data) == dict:
                if data["model"] in self.model_alias:
                    data["model"] = self.model_alias[data["model"]]
            else:
                for i, e in enumerate(data):
                    if e["model"] in self.model_alias:
                        data[i]["model"] = self.model_alias[e["model"]]

        return True

    @deprecation.deprecated()
    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
        previous=None,
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, prepared_tint, box_model = (
            ([], [], [], None) if previous is None else (*previous, None)
        )
        box_model = self.prepare_rendering_data(
            box_model,
            face,
            instance,
            prepared_texture,
            prepared_vertex,
            prepared_tint,
            state,
        )
        return (
            tuple()
            if box_model is None
            else box_model.add_prepared_data_to_batch(
                (prepared_vertex, prepared_texture, prepared_tint, []), batch
            )
        )

    def add_faces_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        faces: int,
        previous=None,
    ) -> typing.Iterable:
        state = instance.get_model_state()
        (
            prepared_vertex,
            prepared_texture,
            prepared_tint,
            prepare_vertex_elements,
            box_model,
        ) = (
            ([], [], [], [], None) if previous is None else (*previous, None)
        )
        box_model = self.prepare_rendering_data_multi_face(
            box_model,
            faces,
            instance,
            prepared_texture,
            prepared_vertex,
            prepared_tint,
            prepare_vertex_elements,
            state,
            batch=batch,
        )
        return (
            tuple()
            if box_model is None
            else box_model.add_prepared_data_to_batch(
                (prepared_vertex, prepared_texture, prepared_tint), batch
            )
        ) + tuple(prepare_vertex_elements)

    @classmethod
    def _test_for(cls, state, part, use_or=False):
        for key in part:
            if use_or:
                if key == "OR":
                    condition = any(
                        [
                            cls._test_for(state, part[key][i], use_or=True)
                            for i in range(len(part[key]))
                        ]
                    )
                else:
                    condition = key in state and (
                        (state[key] not in part[key].split("|"))
                        if type(part[key]) == str
                        else (state[key] == part[key])
                    )
                if condition:
                    return True
            else:
                if key == "OR":
                    condition = not any(
                        [
                            cls._test_for(state, part[key][i], use_or=True)
                            for i in range(len(part[key]))
                        ]
                    )
                else:
                    condition = key not in state or (
                        state[key] not in part[key].split("|")
                        if type(part[key]) == str
                        else state[key] == part[key]
                    )
                if condition:
                    return False
        return not use_or

    def transform_to_bounding_box(
        self, instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget
    ):
        state = instance.get_model_state()
        bbox = mcpython.engine.physics.BoundingBox.BoundingArea()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = decode_entry(data)
                    model = shared.model_handler.models[model]
                    for box_model in model.box_models:
                        bbox.bounding_boxes.append(
                            mcpython.engine.physics.BoundingBox.AxisAlignedBoundingBox(
                                box_model.box_size,
                                box_model.box_position,
                                rotation=config["rotation"],
                            )
                        )
                else:
                    config, model = get_model_choice(data, instance)
                    model = shared.model_handler.models[model]
                    for box_model in model.box_models:
                        bbox.bounding_boxes.append(
                            mcpython.engine.physics.BoundingBox.AxisAlignedBoundingBox(
                                box_model.box_size,
                                box_model.box_position,
                                rotation=config["rotation"],
                            )
                        )
        return bbox

    def draw_face(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        previous=None,
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, prepared_tint, box_model = [], [], [], None
        box_model = self.prepare_rendering_data(
            box_model,
            face,
            instance,
            prepared_texture,
            prepared_vertex,
            prepared_tint,
            state,
        )
        if box_model is not None:
            box_model.draw_prepared_data(
                (prepared_vertex, prepared_texture, prepared_tint, [])
            )

    def draw_face_scaled(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        scale: float,
        previous=None,
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, prepared_tint, box_model = [], [], [], None
        box_model = self.prepare_rendering_data_scaled(
            box_model,
            face,
            instance,
            prepared_texture,
            prepared_vertex,
            prepared_tint,
            state,
            scale,
        )
        if box_model is not None:
            box_model.draw_prepared_data(
                (prepared_vertex, prepared_texture, prepared_tint, [])
            )

    def prepare_rendering_data(
        self,
        box_model,
        face,
        instance: IBlockStateRenderingTarget,
        prepared_texture,
        prepared_vertex,
        prepared_tint,
        state,
    ):
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = decode_entry(data)
                    if model not in shared.model_handler.models:
                        continue
                    _, box_model = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(
                        instance,
                        instance.position,
                        config,
                        face,
                        previous=(prepared_vertex, prepared_texture, prepared_tint),
                    )
                else:
                    config, model = get_model_choice(data, instance)
                    _, box_model = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(
                        instance,
                        instance.position,
                        config,
                        face,
                        previous=(prepared_vertex, prepared_texture, prepared_tint),
                    )
        return box_model

    def prepare_rendering_data_multi_face(
        self,
        box_model,
        faces: int,
        instance: IBlockStateRenderingTarget,
        prepared_texture,
        prepared_vertex,
        prepared_tint,
        prepare_vertex_elements,
        state,
        batch: pyglet.graphics.Batch = None,
    ):
        for entry in self.data["multipart"]:
            # todo: can we do some more clever lookup here?

            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = decode_entry(data)
                    if model not in shared.model_handler.models:
                        continue

                    _, box_model = shared.model_handler.models[
                        model
                    ].prepare_rendering_data_multi_face(
                        instance,
                        instance.position,
                        config,
                        faces,
                        previous=(
                            prepared_vertex,
                            prepared_texture,
                            prepared_tint,
                            prepare_vertex_elements,
                        ),
                        batch=batch,
                    )

                else:
                    config, model = get_model_choice(data, instance)
                    _, box_model = shared.model_handler.models[
                        model
                    ].prepare_rendering_data_multi_face(
                        instance,
                        instance.position,
                        config,
                        faces,
                        previous=(
                            prepared_vertex,
                            prepared_texture,
                            prepared_tint,
                            prepare_vertex_elements,
                        ),
                        batch=batch,
                    )

        return box_model

    def prepare_rendering_data_scaled(
        self,
        box_model,
        face,
        instance: IBlockStateRenderingTarget,
        prepared_texture,
        prepared_vertex,
        prepared_tint,
        state,
        scale: float,
    ):
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = decode_entry(data)
                    if model not in shared.model_handler.models:
                        continue
                    _, box_model = shared.model_handler.models[
                        model
                    ].get_prepared_data_for_scaled(
                        instance,
                        instance.position,
                        config,
                        face,
                        scale,
                        previous=(prepared_vertex, prepared_texture, prepared_tint),
                    )
                else:
                    config, model = get_model_choice(data, instance)
                    _, box_model = shared.model_handler.models[
                        model
                    ].get_prepared_data_for_scaled(
                        instance,
                        instance.position,
                        config,
                        face,
                        scale,
                        previous=(prepared_vertex, prepared_texture, prepared_tint),
                    )
        return box_model


class DefaultDecoder(IBlockStateDecoder):
    """
    Decoder for mc block state files.
    WARNING: the following decoder has some extended features:
    entry parent: An parent DefaultDecoded blockstate from which states and model aliases should be copied
    entry alias: An dict of original -> aliased model to transform any model name of this kind in the system with the given model.
    Alias names MUST start with "alias:"

    todo: add better lookup system for variants
    """

    __slots__ = IBlockStateDecoder.__slots__ + ("parent", "model_alias", "states")

    NAME = "minecraft:default_blockstate_loader"

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        return (
            "variants" in data
            and "forge_marker" not in data
            and "mod_marker" not in data
        )

    def __init__(self, block_state):
        super().__init__(block_state)
        self.parent = None
        self.model_alias = None
        self.states = []

    def parse_data(self, data: dict):
        self.data = data

        for element in data["variants"].keys():
            if element.count("=") > 0:
                keymap = {}
                for e in element.split(","):
                    keymap[e.split("=")[0]] = e.split("=")[1]
            else:
                keymap = {}

            self.states.append(
                (keymap, BlockState().parse_data(data["variants"][element]))
            )

        self.model_alias = {}
        self.parent = None

        if "parent" in data:
            self.parent = data["parent"]
            BlockStateContainer.NEEDED.add(self.parent)

        if "alias" in data:
            self.model_alias = data["alias"]

    async def bake(self):
        if self.parent is not None and isinstance(self.parent, str):
            parent: BlockStateContainer = await BlockStateContainer.get_or_load(
                self.parent
            )
            if not parent.baked:
                return False

            if not isinstance(parent.loader, type(self)):
                raise ValueError("parent must be subclass of start")

            self.parent = parent

            # todo: merge the other way round! (both parts)
            self.model_alias.update(self.parent.loader.model_alias.copy())
            self.states += [(e, state.copy()) for e, state in self.parent.loader.states]

        for model in self.model_alias.values():
            shared.model_handler.used_models.add(model)

        for _, state in self.states:
            state: BlockState
            for i, (model, *d) in enumerate(state.models):

                # resolve the whole alias tree
                # todo: check for cyclic resolve trees
                while model in self.model_alias:
                    state.models[i] = (self.model_alias[model],) + tuple(d)

                    # check if the same model is used
                    if state.models[i][0] == model:
                        break

                    model = state.models[i][0]

        return True

    @deprecation.deprecated()
    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
    ):
        data = instance.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                return blockstate.add_face_to_batch(instance, batch, face)

        if not shared.model_handler.hide_blockstate_errors:
            logger.println(
                "[WARN][INVALID] invalid state mapping for block {}: {} (possible: {})".format(
                    instance, data, [e[0] for e in self.states]
                )
            )

        return tuple()

    def add_faces_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        faces: int,
    ) -> typing.Iterable:
        data = instance.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                return blockstate.add_faces_to_batch(instance, batch, faces)

        if not shared.model_handler.hide_blockstate_errors:
            logger.println(
                "[WARN][INVALID] invalid state mapping for block {}: {} (possible: {})".format(
                    instance, data, [e[0] for e in self.states]
                )
            )

        return tuple()

    def add_raw_face_to_batch(
        self, instance: IBlockStateRenderingTarget, position, state, batches, face
    ):
        state = state
        for keymap, blockstate in self.states:
            if keymap == state:
                return blockstate.add_raw_face_to_batch(
                    instance, position, batches, face
                )

        if not shared.model_handler.hide_blockstate_errors:
            logger.println(
                "[WARN][INVALID] invalid state mapping for block {}: {} (possible: {}".format(
                    position, state, [e[0] for e in self.states]
                )
            )

        return tuple()

    def transform_to_bounding_box(
        self, instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget
    ):
        if instance.block_state is None:
            instance.block_state = 0
        data = instance.get_model_state()
        bbox = mcpython.engine.physics.BoundingBox.BoundingArea()

        for keymap, blockstate in self.states:
            if keymap == data:
                model, config, _ = blockstate.models[instance.block_state]
                model = shared.model_handler.models[model]
                for box_model in model.box_models:
                    rotation = config["rotation"]
                    bbox.bounding_boxes.append(
                        mcpython.engine.physics.BoundingBox.AxisAlignedBoundingBox(
                            box_model.box_size,
                            box_model.box_position,
                            rotation=rotation,
                        )
                    )

        return bbox

    def draw_face(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        data = instance.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                blockstate.draw_face(instance, face)
                return

        if not shared.model_handler.hide_blockstate_errors:
            logger.println(
                "[WARN][INVALID] invalid state mapping for block {} at {}: {} (possible: {}".format(
                    instance.NAME, instance.position, data, [e[0] for e in self.states]
                )
            )

    def draw_face_scaled(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        scale: float,
    ):
        data = instance.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                blockstate.draw_face_scaled(instance, face, scale)
                return

        if not shared.model_handler.hide_blockstate_errors:
            logger.println(
                "[WARN][INVALID] invalid state mapping for block {} at {}: {} (possible: {}".format(
                    instance.NAME, instance.position, data, [e[0] for e in self.states]
                )
            )


if shared.IS_CLIENT:
    shared.registry(MultiPartDecoder)
    shared.registry(DefaultDecoder)


class BlockStateContainer:
    TO_CREATE = set()
    LOOKUP_DIRECTORIES = set()
    RAW_DATA = []
    NEEDED = set()  # for parent <-> child connection

    @classmethod
    async def from_directory(cls, directory: str, modname: str, immediate=False):
        for file in await mcpython.engine.ResourceLoader.get_all_entries(directory):
            if not file.endswith("/"):
                await cls.from_file(file, modname, immediate=immediate)

        cls.LOOKUP_DIRECTORIES.add((directory, modname))

    @classmethod
    async def from_file(cls, file: str, modname: str, immediate=False):
        # todo: check for correct process
        if immediate:
            await cls.unsafe_from_file(file)
        else:
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:model:blockstate_create",
                cls.unsafe_from_file(file),
                info="loading block state file '{}'".format(file),
            )
        cls.TO_CREATE.add(file)

    @classmethod
    async def unsafe_from_file(cls, file: str):
        try:
            s = file.split("/")
            modname = s[s.index("blockstates") - 1]
            return await cls("{}:{}".format(modname, s[-1].split(".")[0])).parse_data(
                await mcpython.engine.ResourceLoader.read_json(file)
            )
        except BlockStateNotNeeded:
            pass
        except:
            logger.print_exception(
                "error during loading model from file '{}'".format(file)
            )

    @classmethod
    async def from_data(
        cls,
        name: str,
        data: typing.Dict[str, typing.Any],
        immediate=False,
        store=True,
        force=False,
    ):
        assert isinstance(name, str), "name must be str"

        # todo: check for correct process
        if store:
            cls.RAW_DATA.append((name, data, force))

        if immediate:
            await cls.unsafe_from_data(name, data, force=force)
        else:
            mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
                "stage:model:blockstate_create",
                cls.unsafe_from_data(name, data),
                info="loading block state '{}' from raw data".format(name),
                force=force,
            )

    @classmethod
    async def unsafe_from_data(
        cls, name: str, data: typing.Dict[str, typing.Any], immediate=False, force=False
    ):
        assert isinstance(name, str), "name must be str"
        try:
            instance = await cls(name, immediate=immediate, force=force).parse_data(
                data
            )
            await instance.bake()
            return instance
        except BlockStateNotNeeded:
            pass  # do we need this model?
        except:
            logger.print_exception(
                "error during loading model for '{}' from data {}".format(name, data)
            )

    @classmethod
    async def get_or_load(cls, name: str) -> "BlockStateContainer":
        if name in shared.model_handler.blockstates:
            return shared.model_handler.blockstates[name]

        file = "assets/{}/blockstates/{}.json".format(*name.split(":"))
        if not await mcpython.engine.ResourceLoader.exists(file):
            raise FileNotFoundError("for blockstate file named '{}'".format(name))

        data = await mcpython.engine.ResourceLoader.read_json(file)
        return await cls.unsafe_from_data(name, data, immediate=True, force=True)

    __slots__ = ("name", "loader", "baked")

    def __init__(self, name: str, immediate=False, force=False):
        assert isinstance(name, str), "name must be str"

        self.name = name
        if (
            (
                name not in shared.registry.get_by_name("minecraft:block").entries
                and name not in self.NEEDED
            )
            and name != "minecraft:missing_texture"
            and not force
        ):
            raise BlockStateNotNeeded()

        shared.model_handler.blockstates[name] = self
        self.loader = None

        self.baked = False

        if not immediate and not shared.mod_loader.finished:
            shared.mod_loader.mods[name.split(":")[0]].eventbus.subscribe(
                "stage:model:blockstate_bake",
                self.bake(),
                info="baking block state {}".format(name),
            )
        else:
            shared.tick_handler.schedule_once(self.bake())

    async def parse_data(self, data: dict):
        for loader in blockstate_decoder_registry.entries.values():
            if loader.is_valid(data):
                self.loader: IBlockStateDecoder = loader(self)
                try:
                    self.loader.parse_data(data)
                except:
                    logger.print_exception(
                        f"block state loader {loader.NAME} failed to load block state {self.name}; continuing further search"
                    )
                break
        else:
            logger.println(
                "can't find matching loader for block state {}".format(self.name)
            )

        return self

    async def bake(self):
        try:
            if self.loader and not await self.loader.bake():
                shared.mod_loader.mods[self.name.split(":")[0]].eventbus.subscribe(
                    "stage:model:blockstate_bake",
                    self.bake,
                    info="loading block state {}".format(self.name),
                )
            else:
                self.baked = True
        except:
            logger.print_exception("during baking block state " + self.name)
            self.baked = True

    @deprecation.deprecated()
    def add_face_to_batch(self, block, batch, face):
        return self.loader.add_face_to_batch(block, batch, face)

    def add_faces_to_batch(
        self,
        block: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        faces: int,
    ):
        return self.loader.add_faces_to_batch(block, batch, faces)

    def add_raw_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position: tuple,
        state,
        batches,
        face,
    ):
        return self.loader.add_raw_face_to_batch(
            instance, position, state, batches, face
        )

    def draw_face(
        self,
        block: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        self.loader.draw_face(block, face)

    def draw_face_scaled(
        self,
        block: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        scale: float,
    ):
        self.loader.draw_face_scaled(block, face, scale)


class BlockState:
    """
    Container holding a single block state link
    todo: don't store the raw data
    """

    __slots__ = ("data", "models")

    def __init__(self):
        self.data = None
        self.models = []  # (model, config, weight)

    def parse_data(self, data: dict):
        self.data = data

        if type(data) == dict:
            if "model" in data:
                self.models.append(decode_entry(data))
                shared.model_handler.used_models.add(data["model"])

        elif type(data) == list:
            models = [decode_entry(x) for x in data]
            self.models += models
            shared.model_handler.used_models |= set([x[0] for x in models])

        return self

    def copy(self):
        return BlockState().parse_data(copy.deepcopy(self.data))

    @deprecation.deprecated()
    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
    ):
        return self.add_faces_to_batch(instance, batch, face.bitflag)

    def add_faces_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        faces: int,
    ):
        if (
            instance.block_state is None
            or instance.block_state < 0
            or instance.block_state > len(self.models)
        ):
            instance.block_state = self.models.index(
                random.choices(self.models, [e[2] for e in self.models])[0]
            )

        model, config, _ = self.models[instance.block_state]
        if model not in shared.model_handler.models:
            if not shared.model_handler.hide_blockstate_errors:
                logger.println(
                    "can't find model named '{}' to add at {}".format(
                        model, instance.position
                    )
                )

            return tuple()

        m = shared.model_handler.models[model]

        if m is None:
            return tuple()

        result = m.add_faces_to_batch(instance, instance.position, batch, config, faces)
        return result

    def add_raw_face_to_batch(
        self, instance: IBlockStateRenderingTarget, position, batches, face
    ):
        block_state = self.models.index(
            random.choices(self.models, [e[2] for e in self.models])[0]
        )
        model, config, _ = self.models[block_state]
        if model not in shared.model_handler.models:
            if not shared.model_handler.hide_blockstate_errors:
                logger.println(
                    "can't find model named '{}' to add at {}".format(model, position)
                )
            return tuple()
        result = shared.model_handler.models[model].add_face_to_batch(
            instance, position, batches, config, face
        )
        return result

    def draw_face(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        if instance.block_state is None:
            instance.block_state = self.models.index(
                random.choices(self.models, [e[2] for e in self.models])[0]
            )
        model, config, _ = self.models[instance.block_state]
        if model not in shared.model_handler.models:
            if not shared.model_handler.hide_blockstate_errors:
                logger.println(
                    "can't find model named '{}' to add at {}".format(
                        model, instance.position
                    )
                )
            return
        shared.model_handler.models[model].draw_face(
            instance, instance.position, config, face
        )

    def draw_face_scaled(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        scale: float,
    ):
        if instance.block_state is None:
            instance.block_state = self.models.index(
                random.choices(self.models, [e[2] for e in self.models])[0]
            )
        model, config, _ = self.models[instance.block_state]
        if model not in shared.model_handler.models:
            if not shared.model_handler.hide_blockstate_errors:
                logger.println(
                    "can't find model named '{}' to add at {}".format(
                        model, instance.position
                    )
                )
            return
        shared.model_handler.models[model].draw_face_scaled(
            instance,
            instance.position,
            config,
            face,
            scale=scale,
        )


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:blockstate_search",
    BlockStateContainer.from_directory("assets/minecraft/blockstates", "minecraft"),
    info="searching for block states",
)
