"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.ResourceLocator
import random
import mcpython.common.mod.ModMcpython
import mcpython.common.event.Registry
import mcpython.common.block.BoundingBox
import copy


class BlockStateNotNeeded(Exception):
    pass


class IBlockStateDecoder(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:blockstate"

    # for developers of mods: add an entry called "mod_marker" storing the mod name the loader is implemented in and
    # check for it here
    @classmethod
    def is_valid(cls, data: dict) -> bool:
        raise NotImplementedError()

    def __init__(self, data: dict, block_state):
        self.data = data
        self.block_state = block_state

    def add_face_to_batch(self, block, batch, face) -> list:
        raise NotImplementedError()

    def transform_to_hitbox(
        self, block
    ):  # optional: transforms the BlockState into an BoundingBox-like objects
        pass

    def draw_face(
        self, block, face
    ):  # optional: draws the BlockState direct without an batch
        pass

    def bake(self) -> bool:
        """
        Called when it is time to bake it
        :return: if it was successful or not
        """
        return True


blockstatedecoderregistry = mcpython.common.event.Registry.Registry(
    "blockstates", ["minecraft:blockstate"]
)


@G.registry
class MultiPartDecoder(IBlockStateDecoder):
    """
    Decoder for mc multipart state files.
    WARNING: the following decoder has some extended features:
    entry parent: An parent DefaultDecoded blockstate from which states and model aliases should be copied
    entry alias: An dict of original -> aliased model to transform any model name of this kind in the system with the given model. Alias names MUST start with alias:

    todo: can we optimize it by pre-doing some stuff?
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
                G.modelhandler.used_models.append(entry["apply"]["model"])
            else:
                for d in entry["apply"]:
                    G.modelhandler.used_models.append(d["model"])
        self.model_alias = {}
        self.parent = None
        if "parent" in data:
            self.parent = data["parent"]
            BlockStateDefinition.NEEDED.add(self.parent)
        if "alias" in data:
            self.model_alias = data["alias"]

    def bake(self):
        if self.parent is not None:
            if self.parent not in G.modelhandler.blockstates:
                raise ValueError(
                    "block state referencing '{}' is invalid!".format(self.parent)
                )
            parent: BlockStateDefinition = G.modelhandler.blockstates[self.parent]
            if not parent.baked:
                return False
            if not issubclass(type(parent.loader), type(self)):
                raise ValueError("parent must be subclass of start")
            self.parent = parent
            self.model_alias.update(self.parent.loader.model_alias.copy())
            self.data["multipart"].extend(
                copy.deepcopy(self.parent.loader.data["multipart"])
            )
        for model in self.model_alias.values():
            G.modelhandler.used_models.append(model)
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

    def add_face_to_batch(self, block, batch, face):
        state = block.get_model_state()
        result = []
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    if model not in G.modelhandler.models:
                        continue
                    result += G.modelhandler.models[model].add_face_to_batch(
                        block.position, batch, config, face
                    )
                else:
                    if block.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[block.block_state]
                        )
                    result += G.modelhandler.models[model].add_face_to_batch(
                        block.position, batch, config, face
                    )
        return result

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

    def transform_to_hitbox(self, blockinstance):
        state = blockinstance.get_model_state()
        bbox = mcpython.common.block.BoundingBox.BoundingArea()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    model = G.modelhandler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bboxes.append(
                            mcpython.common.block.BoundingBox.BoundingBox(
                                tuple([e / 16 for e in boxmodel.boxsize]),
                                tuple([e / 16 for e in boxmodel.rposition]),
                                rotation=config["rotation"],
                            )
                        )
                else:
                    if blockinstance.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        mcpython.block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[blockinstance.block_state]
                        )
                    model = G.modelhandler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bboxes.append(
                            mcpython.common.block.BoundingBox.BoundingBox(
                                tuple([e / 16 for e in boxmodel.boxsize]),
                                tuple([e / 16 for e in boxmodel.rposition]),
                                rotation=config["rotation"],
                            )
                        )
        return bbox

    def draw_face(self, block, face):
        state = block.get_model_state()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    G.modelhandler.models[model].draw_face(block.position, config, face)
                else:
                    if block.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(
                            entries, weights=[e[2] for e in entries]
                        )[0]
                        block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(
                            data[block.block_state]
                        )
                    G.modelhandler.models[model].draw_face(block.position, config, face)


@G.registry
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
        if self.parent is not None:
            if self.parent not in G.modelhandler.blockstates:
                print("block state referencing '{}' is invalid!".format(self.parent))
                return
            parent: BlockStateDefinition = G.modelhandler.blockstates[self.parent]
            if not parent.baked:
                return False
            if not issubclass(type(parent.loader), type(self)):
                raise ValueError("parent must be subclass of start")
            self.parent = parent
            self.model_alias.update(self.parent.loader.model_alias.copy())
            self.states += [(e, state.copy()) for e, state in self.parent.loader.states]
        for model in self.model_alias.values():
            G.modelhandler.used_models.append(model)
        for _, state in self.states:
            state: BlockState
            for i, (model, *d) in enumerate(state.models):
                if model in self.model_alias:
                    state.models[i] = (self.model_alias[model],) + tuple(d)
        return True

    def add_face_to_batch(self, block, batch, face):
        data = block.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                return blockstate.add_face_to_batch(block, batch, face)
        logger.println("[WARN][INVALID] invalid state mapping for block {}: {} (possible: {}".format(
            block, data, [e[0] for e in self.states]
        ))
        return []

    def transform_to_hitbox(self, blockinstance):
        if blockinstance.block_state is None:
            blockinstance.block_state = 0
        data = blockinstance.get_model_state()
        bbox = mcpython.common.block.BoundingBox.BoundingArea()
        for keymap, blockstate in self.states:
            if keymap == data:
                model, config, _ = blockstate.models[blockinstance.block_state]
                model = G.modelhandler.models[model]
                for boxmodel in model.boxmodels:
                    rotation = config["rotation"]
                    bbox.bboxes.append(
                        mcpython.common.block.BoundingBox.BoundingBox(
                            tuple([e / 16 for e in boxmodel.boxsize]),
                            tuple([e / 16 for e in boxmodel.rposition]),
                            rotation=rotation,
                        )
                    )
        return bbox

    def draw_face(self, block, face):
        data = block.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                blockstate.draw_face(block, face)
                return
        logger.println("[WARN][INVALID] invalid state mapping for block {} at {}: {} (possible: {}".format(
            block.NAME, block.position, data, [e[0] for e in self.states]
        ))


class BlockStateDefinition:
    TO_CREATE = set()
    LOOKUP_DIRECTORIES = set()
    NEEDED = set()  # for parent <-> child connection

    @classmethod
    def from_directory(cls, directory: str, modname: str, immediate=False):
        for file in mcpython.ResourceLocator.get_all_entries(directory):
            if not file.endswith("/"):
                cls.from_file(file, modname, immediate=immediate)
        cls.LOOKUP_DIRECTORIES.add((directory, modname))

    @classmethod
    def from_file(cls, file: str, modname: str, immediate=False):
        if immediate:
            cls._from_file(file)
        else:
            G.modloader.mods[modname].eventbus.subscribe(
                "stage:model:blockstate_create",
                cls._from_file,
                file,
                info="loading block state {}".format(file),
            )
        cls.TO_CREATE.add(file)

    @classmethod
    def _from_file(cls, file: str):
        try:
            s = file.split("/")
            modname = s[s.index("blockstates") - 1]
            return BlockStateDefinition(
                mcpython.ResourceLocator.read(file, "json"),
                "{}:{}".format(modname, s[-1].split(".")[0]),
            )
        except BlockStateNotNeeded:
            pass
        except:
            logger.print_exception(
                "error during loading model from file '{}'".format(file)
            )

    @classmethod
    def from_data(cls, name, data):
        mcpython.mod.ModMcpython.mcpython.eventbus.subscribe(
            "stage:model:blockstate_create",
            cls._from_data,
            name,
            data,
            info="loading block state {}".format(name),
        )

    @classmethod
    def _from_data(cls, name, data):
        try:
            return BlockStateDefinition(data, name)
        except BlockStateNotNeeded:
            pass  # do we need this model?
        except:
            logger.print_exception(
                "error during loading model for '{}' from data {}".format(name, data)
            )

    def __init__(self, data: dict, name: str):
        self.name = name
        if (
            name not in G.registry.get_by_name("block").registered_object_map
            and name not in self.NEEDED
        ):
            raise BlockStateNotNeeded()
        G.modelhandler.blockstates[name] = self
        self.loader = None
        for loader in blockstatedecoderregistry.registered_object_map.values():
            if loader.is_valid(data):
                self.loader = loader(data, self)
                break
        else:
            raise ValueError("can't find matching loader for model {}".format(name))
        self.baked = False

        G.modloader.mods[name.split(":")[0]].eventbus.subscribe(
            "stage:model:blockstate_bake",
            self.bake,
            info="baking block state {}".format(name),
        )

    def bake(self):
        if not self.loader.bake():
            G.modloader.mods[self.name.split(":")[0]].eventbus.subscribe(
                "stage:model:blockstate_bake",
                self.bake,
                info="loading block state {}".format(self.name),
            )
        else:
            self.baked = True

    def add_face_to_batch(self, block, batch, face):
        return self.loader.add_face_to_batch(block, batch, face)

    def draw_face(self, block, face):
        self.loader.draw_face(block, face)


class BlockState:
    def __init__(self, data):
        self.data = data
        self.models = []  # (model, config, weight)
        if type(data) == dict:
            if "model" in data:
                self.models.append(self.decode_entry(data))
                G.modelhandler.used_models.append(data["model"])
        elif type(data) == list:
            models = [self.decode_entry(x) for x in data]
            self.models += models
            G.modelhandler.used_models += [x[0] for x in models]

    def copy(self):
        return BlockState(self.data)

    @staticmethod
    def decode_entry(data: dict):
        model = data["model"]
        G.modelhandler.used_models.append(model)
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

    def add_face_to_batch(self, block, batch, face):
        if (
            block.block_state is None
            or block.block_state < 0
            or block.block_state > len(self.models)
        ):
            block.block_state = self.models.index(
                random.choices(self.models, [e[2] for e in self.models])[0]
            )
        result = []
        model, config, _ = self.models[block.block_state]
        if model not in G.modelhandler.models:
            logger.println("can't find model named '{}' to add at {}".format(model, block.position))
            return result
        result += G.modelhandler.models[model].add_face_to_batch(
            block.position, batch, config, face
        )
        return result

    def draw_face(self, block, face):
        if block.block_state is None:
            block.block_state = self.models.index(
                random.choices(self.models, [e[2] for e in self.models])[0]
            )
        model, config, _ = self.models[block.block_state]
        if model not in G.modelhandler.models:
            raise ValueError(
                "can't find model named '{}' to draw at {}".format(
                    model, block.position
                )
            )
        G.modelhandler.models[model].draw_face(block.position, config, face)


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:model:blockstate_search",
    BlockStateDefinition.from_directory,
    "assets/minecraft/blockstates",
    "minecraft",
    info="searching for block states",
)
