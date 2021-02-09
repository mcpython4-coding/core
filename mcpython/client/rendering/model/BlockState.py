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
import typing
import copy

import pyglet

from mcpython import shared, logger
import mcpython.ResourceLoader
import random
import mcpython.common.mod.ModMcpython
import mcpython.common.event.Registry
import mcpython.common.block.BoundingBox
import copy
import mcpython.client.rendering.model.api
import mcpython.util.enums


class BlockStateNotNeeded(Exception):
    pass


class IBlockStateDecoder(mcpython.common.event.Registry.IRegistryContent):
    """
    Abstract base class for block state decoders

    Identification of files to decode:
        bool(is_valid(data)) == True, where data is the loaded json data
        for developers of mods: add an entry called "mod_marker" storing the mod name the loader is implemented in and
            check for it here

    Loading:
        __init__(data, BlockStateDefinition) -> Instance

    Baking:
        bake() is called to bake references and do similar stuff, returning success or not

    Drawing:
        add_face_to_batch() should add the given face to the batches given
        add_raw_face_to_batch() should add a face to the batch without the block instance, but instead the position
        draw() should draw the block in-place

    todo: add draw variant for raw
    todo: add data getter functions for better performance
    todo: cache non-offset data from models per state for faster drawing
    todo: can we do something rendering wise which will make it efficient to draw multiple same blocks
    todo: block batches should be selected before, based on a property on block class
    """

    TYPE = "minecraft:blockstate"

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        raise NotImplementedError()

    def __init__(self, data: dict, block_state: "BlockStateDefinition"):
        self.data = data
        self.block_state = block_state

    def bake(self) -> bool:
        return True

    def add_face_to_batch(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
    ) -> list:
        raise NotImplementedError()

    def add_raw_face_to_batch(self, position, state, batches, faces):
        return tuple()

    def draw_face(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):  # optional: draws the BlockState direct without an batch
        pass

    def transform_to_hitbox(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
    ):  # optional: transforms the BlockState into an BoundingBox-like objects
        pass


blockstate_decoder_registry = mcpython.common.event.Registry.Registry(
    "minecraft:blockstates",
    ["minecraft:blockstate"],
    "stage:blockstate:register_loaders",
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

    def __init__(self, data: dict, block_state):
        super().__init__(data, block_state)
        for entry in data["multipart"]:
            if type(entry["apply"]) == dict:
                shared.model_handler.used_models.add(entry["apply"]["model"])
            else:
                for d in entry["apply"]:
                    shared.model_handler.used_models.add(d["model"])

        self.model_alias = {}
        self.parent: typing.Union[str, "BlockStateDefinition", None] = None

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

            if not issubclass(type(parent.loader), type(self)):
                raise ValueError(
                    "parent must be subclass of the current loader ({} is not a subclass of {})".format(
                        type(self), type(parent.loader)
                    )
                )

            self.parent = parent
            self.model_alias.update(self.parent.loader.model_alias.copy())
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
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, boxmodel = [], [], None
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    if model not in shared.model_handler.models:
                        continue
                    (a, b), boxmodel = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(instance.position, config, face)
                    prepared_vertex.extend(a)
                    prepared_texture.extend(b)
                else:
                    if instance.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        instance.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[instance.block_state]
                        )
                    (a, b), boxmodel = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(instance.position, config, face)
                    prepared_vertex.extend(a)
                    prepared_texture.extend(b)
        return (
            tuple()
            if boxmodel is None
            else boxmodel.add_prepared_data_to_batch(
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

    def transform_to_hitbox(
        self, instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget
    ):
        state = instance.get_model_state()
        bbox = mcpython.common.block.BoundingBox.BoundingArea()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    model = shared.model_handler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bounding_boxes.append(
                            mcpython.common.block.BoundingBox.BoundingBox(
                                tuple([e / 16 for e in boxmodel.box_size]),
                                tuple([e / 16 for e in boxmodel.relative_position]),
                                rotation=config["rotation"],
                            )
                        )
                else:
                    if instance.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        instance.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[instance.block_state]
                        )
                    model = shared.model_handler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bounding_boxes.append(
                            mcpython.common.block.BoundingBox.BoundingBox(
                                tuple([e / 16 for e in boxmodel.box_size]),
                                tuple([e / 16 for e in boxmodel.relative_position]),
                                rotation=config["rotation"],
                            )
                        )
        return bbox

    def draw_face(
        self,
        instance: mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        state = instance.get_model_state()
        prepared_vertex, prepared_texture, boxmodel = [], [], None
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    if model not in shared.model_handler.models:
                        continue
                    (a, b), boxmodel = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(instance.position, config, face)
                    prepared_vertex.extend(a)
                    prepared_texture.extend(b)
                else:
                    if instance.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        instance.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[instance.block_state]
                        )
                    (a, b), boxmodel = shared.model_handler.models[
                        model
                    ].get_prepared_data_for(instance.position, config, face)
                    prepared_vertex.extend(a)
                    prepared_texture.extend(b)
        if boxmodel is not None:
            boxmodel.draw_prepared_data((prepared_vertex, prepared_texture))


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

    def __init__(self, data: dict, block_state):
        super().__init__(data, block_state)
        self.states = []

        for element in data["variants"].keys():
            if element.count("=") > 0:
                keymap = {}
                for e in element.split(","):
                    keymap[e.split("=")[0]] = e.split("=")[1]
            else:
                keymap = {}

            self.states.append((keymap, BlockState(data["variants"][element])))

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

    def transform_to_hitbox(
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
                for boxmodel in model.boxmodels:
                    rotation = config["rotation"]
                    bbox.bounding_boxes.append(
                        mcpython.common.block.BoundingBox.BoundingBox(
                            tuple([e / 16 for e in boxmodel.box_size]),
                            tuple([e / 16 for e in boxmodel.relative_position]),
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
        for file in mcpython.ResourceLoader.get_all_entries(directory):
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
            return BlockStateDefinition(
                mcpython.ResourceLoader.read_json(file),
                "{}:{}".format(modname, s[-1].split(".")[0]),
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
                data, name, immediate=immediate, force=force
            )
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
        if not mcpython.ResourceLoader.exists(file):
            raise FileNotFoundError("for blockstate '{}'".format(name))

        data = mcpython.ResourceLoader.read_json(file)
        return cls.unsafe_from_data(name, data, immediate=True, force=True)

    def __init__(self, data: dict, name: str, immediate=False, force=False):
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
        for loader in blockstate_decoder_registry.entries.values():
            if loader.is_valid(data):
                self.loader = loader(data, self)
                break
        else:
            raise ValueError("can't find matching loader for model {}".format(name))
        self.baked = False

        if not immediate:
            shared.mod_loader.mods[name.split(":")[0]].eventbus.subscribe(
                "stage:model:blockstate_bake",
                self.bake,
                info="baking block state {}".format(name),
            )
        else:
            self.bake()

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
    @staticmethod
    def decode_entry(data: typing.Dict[str, typing.Any]):
        model = data["model"]
        shared.model_handler.used_models.add(model)
        rotations = (
            data["x"] if "x" in data else 0,
            data["y"] if "y" in data else 0,
            data["z"] if "z" in data else 0,
        )
        return (
            model,
            {"rotation": rotations, "uv_lock": data.setdefault("uvlock", False)},
            1 if "weight" not in data else data["weight"],
        )

    def __init__(self, data: dict):
        self.data = data
        self.models = []  # (model, config, weight)
        if type(data) == dict:
            if "model" in data:
                self.models.append(self.decode_entry(data))
                shared.model_handler.used_models.add(data["model"])
        elif type(data) == list:
            models = [self.decode_entry(x) for x in data]
            self.models += models
            shared.model_handler.used_models |= set([x[0] for x in models])

    def copy(self):
        return BlockState(copy.deepcopy(self.data))

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
