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
import copy
import random
import typing

import mcpython.client.rendering.model.api
import mcpython.common.block.BoundingBox
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.api import BlockStateNotNeeded, IBlockStateDecoder
from mcpython.client.rendering.model.util import decode_entry, get_model_choice
from mcpython.engine import logger

blockstate_decoder_registry = mcpython.common.event.Registry.Registry(
    "minecraft:blockstates",
    ["minecraft:blockstate"],
    "stage:blockstate:register_loaders",
    sync_via_network=False,
)


@shared.registry
class MultiPartDecoder(IBlockStateDecoder):
    """
    Decoder for mc multipart state files.
    WARNING: the following decoder has some extended features:
    entry parent: An parent DefaultDecoded blockstate from which states and model aliases should be copied
    entry alias: An dict of original -> aliased model to transform any model name of this kind in the system with the given model. Alias names MUST start with alias:

    todo: can we optimize it by pre-doing some stuff?
    todo: fix alias system
    """

    NAME = "minecraft:multipart_blockstate_loader"

    @classmethod
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

    def parse_data(self, data: dict):
        self.data = data
        for entry in data["multipart"]:
            if type(entry["apply"]) == dict:
                shared.model_handler.used_models.add(entry["apply"]["model"])
            else:
                for d in entry["apply"]:
                    shared.model_handler.used_models.add(d["model"])

        self.model_alias: typing.Dict[str, typing.Any] = {}
        self.parent: typing.Union[str, "BlockStateDefinition", None] = None

        if "parent" in data:
            self.parent = data["parent"]
            BlockStateDefinition.NEEDED.add(self.parent)

        if "alias" in data:
            self.model_alias = data["alias"]

    def bake(self):
        if self.parent is not None and isinstance(self.parent, str):
            parent: BlockStateDefinition = BlockStateDefinition.get_or_load(self.parent)

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

    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
        previous=None,
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, box_model = (
            ([], [], None) if previous is None else (*previous, None)
        )
        box_model = self.prepare_rendering_data(
            box_model, face, instance, prepared_texture, prepared_vertex, state
        )
        return (
            tuple()
            if box_model is None
            else box_model.add_prepared_data_to_batch(
                (prepared_vertex, prepared_texture), batch
            )
        )

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
        bbox = mcpython.common.block.BoundingBox.BoundingArea()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = decode_entry(data)
                    model = shared.model_handler.models[model]
                    for box_model in model.box_models:
                        bbox.bounding_boxes.append(
                            mcpython.common.block.BoundingBox.BoundingBox(
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
                            mcpython.common.block.BoundingBox.BoundingBox(
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
        prepared_vertex, prepared_texture, box_model = [], [], None
        box_model = self.prepare_rendering_data(
            box_model, face, instance, prepared_texture, prepared_vertex, state
        )
        if box_model is not None:
            box_model.draw_prepared_data((prepared_vertex, prepared_texture))

    def prepare_rendering_data(
        self, box_model, face, instance, prepared_texture, prepared_vertex, state
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
                        instance.position,
                        config,
                        face,
                        previous=(prepared_vertex, prepared_texture),
                    )
                else:
                    config, model = get_model_choice(data, instance)
                    _, box_model = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(
                        instance.position,
                        config,
                        face,
                        previous=(prepared_vertex, prepared_texture),
                    )
        return box_model


@shared.registry
class DefaultDecoder(IBlockStateDecoder):
    """
    Decoder for mc block state files.
    WARNING: the following decoder has some extended features:
    entry parent: An parent DefaultDecoded blockstate from which states and model aliases should be copied
    entry alias: An dict of original -> aliased model to transform any model name of this kind in the system with the given model. Alias names MUST start with alias:
    """

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
            BlockStateDefinition.NEEDED.add(self.parent)

        if "alias" in data:
            self.model_alias = data["alias"]

    def bake(self):
        if self.parent is not None and isinstance(self.parent, str):
            parent: BlockStateDefinition = BlockStateDefinition.get_or_load(self.parent)
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

    def add_raw_face_to_batch(self, position, state, batches, face):
        state = state
        for keymap, blockstate in self.states:
            if keymap == state:
                return blockstate.add_raw_face_to_batch(position, batches, face)

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
        bbox = mcpython.common.block.BoundingBox.BoundingArea()

        for keymap, blockstate in self.states:
            if keymap == data:
                model, config, _ = blockstate.models[instance.block_state]
                model = shared.model_handler.models[model]
                for box_model in model.box_models:
                    rotation = config["rotation"]
                    bbox.bounding_boxes.append(
                        mcpython.common.block.BoundingBox.BoundingBox(
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


class BlockStateDefinition:
    TO_CREATE = set()
    LOOKUP_DIRECTORIES = set()
    RAW_DATA = []
    NEEDED = set()  # for parent <-> child connection

    @classmethod
    def from_directory(cls, directory: str, modname: str, immediate=False):
        for file in mcpython.engine.ResourceLoader.get_all_entries(directory):
            if not file.endswith("/"):
                cls.from_file(file, modname, immediate=immediate)
        cls.LOOKUP_DIRECTORIES.add((directory, modname))

    @classmethod
    def from_file(cls, file: str, modname: str, immediate=False):
        # todo: check for correct process
        if immediate:
            cls.unsafe_from_file(file)
        else:
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:model:blockstate_create",
                cls.unsafe_from_file,
                file,
                info="loading block state file '{}'".format(file),
            )
        cls.TO_CREATE.add(file)

    @classmethod
    def unsafe_from_file(cls, file: str):
        try:
            s = file.split("/")
            modname = s[s.index("blockstates") - 1]
            return cls("{}:{}".format(modname, s[-1].split(".")[0])).parse_data(
                mcpython.engine.ResourceLoader.read_json(file)
            )
        except BlockStateNotNeeded:
            pass
        except:
            logger.print_exception(
                "error during loading model from file '{}'".format(file)
            )

    @classmethod
    def from_data(
        cls,
        name: str,
        data: typing.Dict[str, typing.Any],
        immediate=False,
        store=True,
        force=False,
    ):
        # todo: check for correct process
        if store:
            cls.RAW_DATA.append((data, name, force))
        if immediate:
            cls.unsafe_from_data(name, data, force=force)
        else:
            mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
                "stage:model:blockstate_create",
                cls.unsafe_from_data,
                name,
                data,
                info="loading block state '{}' from raw data".format(name),
                force=force,
            )

    @classmethod
    def unsafe_from_data(
        cls, name: str, data: typing.Dict[str, typing.Any], immediate=False, force=False
    ):
        try:
            instance = BlockStateDefinition(
                name, immediate=immediate, force=force
            ).parse_data(data)
            return instance
        except BlockStateNotNeeded:
            pass  # do we need this model?
        except:
            logger.print_exception(
                "error during loading model for '{}' from data {}".format(name, data)
            )

    @classmethod
    def get_or_load(cls, name: str) -> "BlockStateDefinition":
        if name in shared.model_handler.blockstates:
            return shared.model_handler.blockstates[name]

        file = "assets/{}/blockstates/{}.json".format(*name.split(":"))
        if not mcpython.engine.ResourceLoader.exists(file):
            raise FileNotFoundError("for blockstate '{}'".format(name))

        data = mcpython.engine.ResourceLoader.read_json(file)
        return cls.unsafe_from_data(name, data, immediate=True, force=True)

    def __init__(self, name: str, immediate=False, force=False):
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

        if not immediate:
            shared.mod_loader.mods[name.split(":")[0]].eventbus.subscribe(
                "stage:model:blockstate_bake",
                self.bake,
                info="baking block state {}".format(name),
            )
        else:
            self.bake()

    def parse_data(self, data: dict):
        for loader in blockstate_decoder_registry.entries.values():
            if loader.is_valid(data):
                self.loader: IBlockStateDecoder = loader(self)
                self.loader.parse_data(data)
                break
        else:
            raise ValueError(
                "can't find matching loader for model {}".format(self.name)
            )

        return self

    def bake(self):
        if not self.loader.bake():
            shared.mod_loader.mods[self.name.split(":")[0]].eventbus.subscribe(
                "stage:model:blockstate_bake",
                self.bake,
                info="loading block state {}".format(self.name),
            )
        else:
            self.baked = True

    def add_face_to_batch(
        self,
        block: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
    ):
        return self.loader.add_face_to_batch(block, batch, face)

    def add_raw_face_to_batch(self, position: tuple, state, batches, face):
        return self.loader.add_raw_face_to_batch(position, state, batches, face)

    def draw_face(
        self,
        block: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        self.loader.draw_face(block, face)


class BlockState:
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

    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
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
        result = shared.model_handler.models[model].add_face_to_batch(
            instance.position, batch, config, face
        )
        return result

    def add_raw_face_to_batch(self, position, batches, face):
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
            position, batches, config, face
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
        shared.model_handler.models[model].draw_face(instance.position, config, face)


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:blockstate_search",
    BlockStateDefinition.from_directory,
    "assets/minecraft/blockstates",
    "minecraft",
    info="searching for block states",
)
