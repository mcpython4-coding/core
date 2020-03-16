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
import event.Registry
import block.BoundingBox


class BlockStateNotNeeded(Exception): pass


class IBlockStateDecoder(event.Registry.IRegistryContent):
    TYPE = "minecraft:blockstate"

    # for developers of mods: add an entry called "mod_marker" storing the mod name the loader is implemented in and
    # check for it here
    @classmethod
    def is_valid(cls, data: dict) -> bool: raise NotImplementedError()

    def __init__(self, data: dict, block_state):
        self.data = data
        self.block_state = block_state

    def add_face_to_batch(self, block, batch, face) -> list:
        raise NotImplementedError()

    def transform_to_hitbox(self, block):  # optional: transforms the BlockState into an BoundingBox-like objects
        pass

    def draw_face(self, block, face):  # optional: draws the BlockState direct without an batch
        pass


blockstatedecoderregistry = event.Registry.Registry("blockstates", ["minecraft:blockstate"])


@G.registry
class MultiPartDecoder(IBlockStateDecoder):
    NAME = "minecraft:multipart_blockstate_loader"

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        return "multipart" in data and "forge_marker" not in data and "mod_marker" not in data

    def __init__(self, data: dict, block_state):
        super().__init__(data, block_state)
        for entry in data["multipart"]:
            G.modelhandler.used_models.append(entry["apply"]["model"])

    def add_face_to_batch(self, block, batch, face):
        state = block.get_model_state()
        result = []
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    result += G.modelhandler.models[model].add_face_to_batch(block.position, batch, config, face)
                else:
                    if block.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(entries, weights=[e[2] for e in entries])[0]
                        block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(data[block.block_state])
                    result += G.modelhandler.models[model].add_face_to_batch(block.position, batch, config, face)
        return result

    @classmethod
    def _test_for(cls, state, part, use_or=False):
        for key in part:
            if use_or:
                if key == "OR":
                    condition = any([cls._test_for(state, part[key][i], use_or=True) for i in range(len(part[key]))])
                else:
                    condition = key in state and ((state[key] not in part[key].split("|")) if type(part[key]) == str
                                                  else (state[key] == part[key]))
                if condition: return True
            else:
                if key == "OR":
                    condition = not any([cls._test_for(state, part[key][i], use_or=True) for i in range(len(part[key]))])
                else:
                    condition = key not in state or (state[key] not in part[key].split("|") if type(part[key]) == str
                                                     else state[key] == part[key])
                if condition: return False
        return not use_or

    def transform_to_hitbox(self, blockinstance):
        state = blockinstance.get_model_state()
        bbox = block.BoundingBox.BoundingArea()
        for entry in self.data["multipart"]:
            if "when" not in entry or self._test_for(state, entry["when"]):
                data = entry["apply"]
                if type(data) == dict:
                    model, config, _ = BlockState.decode_entry(data)
                    model = G.modelhandler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bboxes.append(block.BoundingBox.BoundingBox(tuple([e / 16 for e in boxmodel.boxsize]),
                                                                         tuple([e / 16 for e in boxmodel.rposition]),
                                                                         rotation=config["rotation"]))
                else:
                    if blockinstance.block_state is None:
                        entries = [BlockState.decode_entry(e) for e in data]
                        model, config, _ = entry = random.choices(entries, weights=[e[2] for e in entries])[0]
                        block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(data[blockinstance.block_state])
                    model = G.modelhandler.models[model]
                    for boxmodel in model.boxmodels:
                        bbox.bboxes.append(block.BoundingBox.BoundingBox(tuple([e / 16 for e in boxmodel.boxsize]),
                                                                         tuple([e / 16 for e in boxmodel.rposition]),
                                                                         rotation=config["rotation"]))
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
                        model, config, _ = entry = random.choices(entries, weights=[e[2] for e in entries])[0]
                        block.block_state = entries.index(entry)
                    else:
                        model, config, _ = BlockState.decode_entry(data[block.block_state])
                    G.modelhandler.models[model].draw_face(block.position, config, face)


@G.registry
class DefaultDecoder(IBlockStateDecoder):
    NAME = "minecraft:default_blockstate_loader"

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        return "variants" in data and "forge_marker" not in data and "mod_marker" not in data

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

    def add_face_to_batch(self, block, batch, face):
        data = block.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                return blockstate.add_face_to_batch(block, batch, face)
        logger.println("[WARN][INVALID] invalid state mapping for block {} at {}: {} (possible: {}".format(
            block.NAME, block.position, data, [e[0] for e in self.states]))
        return []

    def transform_to_hitbox(self, blockinstance):
        if blockinstance.block_state is None: blockinstance.block_state = 0
        data = blockinstance.get_model_state()
        bbox = block.BoundingBox.BoundingArea()
        for keymap, blockstate in self.states:
            if keymap == data:
                model, config, _ = blockstate.models[blockinstance.block_state]
                model = G.modelhandler.models[model]
                for boxmodel in model.boxmodels:
                    rotation = config["rotation"]
                    bbox.bboxes.append(block.BoundingBox.BoundingBox(tuple([e / 16 for e in boxmodel.boxsize]),
                                                                     tuple([e / 16 for e in boxmodel.rposition]),
                                                                     rotation=rotation))
        return bbox

    def draw_face(self, block, face):
        data = block.get_model_state()
        for keymap, blockstate in self.states:
            if keymap == data:
                blockstate.draw_face(block, face)
                return
        logger.println("[WARN][INVALID] invalid state mapping for block {} at {}: {} (possible: {}".format(
            block.NAME, block.position, data, [e[0] for e in self.states]))


"""
@G.registry
class ForgeVersionDecoder(IBlockStateDecoder):
    @classmethod
    def is_valid(cls, data: dict) -> bool:
        return "forge_marker" in data and data["forge_marker"] == 1 and "mod_marker" not in data

    def __init__(self, data: dict, block_state):
        super().__init__(data, block_state)

    def add_face_to_batch(self, block, batch, face):
        return []

    def transform_to_hitbox(self, block): raise NotImplementedError()"""


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
        if name not in G.registry.get_by_name("block").registered_object_map: raise BlockStateNotNeeded()
        G.modelhandler.blockstates[name] = self
        self.loader = None
        for loader in blockstatedecoderregistry.registered_object_map.values():
            if loader.is_valid(data):
                self.loader = loader(data, self)
                break
        else:
            raise ValueError("can't find matching loader for model {}".format(name))

    def add_face_to_batch(self, block, batch, face): return self.loader.add_face_to_batch(block, batch, face)

    def draw_face(self, block, face): self.loader.draw_face(block, face)


class BlockState:
    def __init__(self, data):
        self.models = []  # (model, config)
        if type(data) == dict:
            if "model" in data:
                self.models.append(self.decode_entry(data))
                G.modelhandler.used_models.append(data["model"])
        elif type(data) == list:
            models = [self.decode_entry(x) for x in data]
            self.models += models
            G.modelhandler.used_models += [x[0] for x in models]

    @staticmethod
    def decode_entry(data: dict):
        model = data["model"]
        G.modelhandler.used_models.append(model)
        rotations = (data["x"] if "x" in data else 0, data["y"] if "y" in data else 0,
                     data["z"] if "z" in data else 0)
        return model, {"rotation": rotations}, 1 if "weight" not in data else data["weight"]

    def add_face_to_batch(self, block, batch, face):
        if block.block_state is None or block.block_state < 0 or block.block_state > len(self.models):
            block.block_state = self.models.index(random.choices(self.models, [e[2] for e in self.models])[0])
        result = []
        model, config, _ = self.models[block.block_state]
        if model not in G.modelhandler.models:
            raise ValueError("can't find model named '{}' to add at {}".format(model, block.position))
        result += G.modelhandler.models[model].add_face_to_batch(block.position, batch, config, face)
        return result

    def draw_face(self, block, face):
        if block.block_state is None:
            block.block_state = self.models.index(random.choices(self.models, [e[2] for e in self.models])[0])
        model, config, _ = self.models[block.block_state]
        if model not in G.modelhandler.models:
            raise ValueError("can't find model named '{}' to draw at {}".format(model, block.position))
        G.modelhandler.models[model].draw_face(block.position, config, face)


mod.ModMcpython.mcpython.eventbus.subscribe("stage:model:blockstate_search", BlockStateDefinition.from_directory,
                                            "assets/minecraft/blockstates", "minecraft",
                                            info="searching for block states")

