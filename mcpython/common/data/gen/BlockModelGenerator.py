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

import mcpython.util.enums
from mcpython.common.data.gen.DataGeneratorManager import (
    DataGeneratorInstance,
    IDataGenerator,
)
from mcpython.engine import logger


def encode_model_key(key):
    if key is None:
        return "default"
    if type(key) == dict:
        return ",".join(["{}={}".format(e, key[e]) for e in key])
    return key


class ModelRepr(IDataGenerator):
    """
    Class for representing an model in an block-state definition generator.
    Rendering is implemented by the respective rendering backend
    """

    @classmethod
    def for_model(cls, model: "BlockModel") -> "ModelRepr":
        return cls(model)

    def __init__(
        self,
        model: typing.Union[str, "BlockModel"],
        r_x=0,
        r_y=0,
        uv_lock=False,
        weight=None,
    ):
        """
        will create an new entry
        :param model: the model to use as e.g. minecraft:block/stone
        :param r_x: the rotation in x direction
        :param r_y: the rotation in y direction
        :param uv_lock: if uv's should be not affected by rotation
        :param weight: the weight, when in an list of multiple models
        """
        self.model = model if type(model) == str else model.name
        self.r_x = r_x % 360
        self.r_y = r_y % 360
        self.uv_lock = uv_lock
        self.weight = weight

        self.generated_cache = (
            None  # holding the data when calling dump() to make later re-use possible
        )

    def dump(self, generator: DataGeneratorInstance) -> dict:
        """
        Will encode your data to an json-able dict
        """
        if self.generated_cache is not None:
            return self.generated_cache
        if ":" not in self.model and generator.default_namespace is not None:
            self.model = "{}:{}".format(generator.default_namespace, self.model)
        data = {
            "model": self.model
            if ":" in self.model or generator.default_namespace is None
            else generator.default_namespace + ":" + self.model
        }
        if self.r_x != 0:
            data["x"] = self.r_x
        if self.r_y != 0:
            data["y"] = self.r_y
        if self.uv_lock is True and (self.r_x or self.r_y):
            data["uvlock"] = self.uv_lock
        if self.weight is not None:
            data["weight"] = self.weight
        self.generated_cache = data
        return data


class SingleFaceConfiguration(IDataGenerator):
    """
    Class for the configuration of one face of an element in an BlockModel
    """

    def __init__(
        self,
        face: typing.Union[str, mcpython.util.enums.EnumSide],
        texture: str,
        uv=(0, 0, 1, 1),
        cull_face: typing.Union[str, mcpython.util.enums.EnumSide] = None,
        rotation=0,
    ):
        """
        Will create an new config
        :param face: the face to configure, as str for face in mcpython.util.enums.EnumSide or an entry of that enum
        :param texture: the texture variable name to use, "#" in front optional (auto-added when not provided)
        :param uv: the uv indexes. when out of the 0-1 bound, behaviour is undefined
        :param cull_face: the cull face of the face. Same parsing as face
        :param rotation: the rotation of the texture as an multiple of 90
        """
        self.face = face if type(face) != str else mcpython.util.enums.EnumSide[face]
        self.texture = texture if texture.startswith("#") else "#" + texture
        self.uv = uv
        if any([e < 0 or e > 1 for e in uv]):
            logger.println(
                "[DATA GEN][WARN] provided uv coordinates for side {} are out of bound".format(
                    face
                )
            )
        if cull_face is None:
            cull_face = self.face
        self.cull_face = (
            cull_face
            if type(cull_face) != str
            else mcpython.util.enums.EnumSide[cull_face]
        )
        if rotation % 90 != 0:
            logger.println(
                "[DATA GEN][WARN] provided non-90-multiple {} for texture rotation for face {}".format(
                    rotation, face
                )
            )
        self.rotation = rotation % 360

        self.generated_cache = None

    def dump(self, generator: DataGeneratorInstance) -> dict:
        """
        Will encode the data into an dict-like object
        """
        if self.generated_cache is not None:
            return self.generated_cache
        data = {"texture": self.texture, "cullface": self.cull_face.normal_name}
        if self.uv != (0, 0, 1, 1):
            data["uv"] = self.uv
        if self.rotation != 0:
            data["rotation"] = self.rotation

        self.generated_cache = data
        return data


class BlockState(IDataGenerator):
    """
    generator class for an block state
    """

    def __init__(self, name: str, parent=None, generate_alias=2):
        self.name = name
        self.states = []
        self.parent = parent
        self.alias = {}
        self.generate_alias = generate_alias

    def add_state(
        self, state: typing.Union[None, str, dict, list, "BlockModel"], *models
    ):
        """
        will add an new possible state into the block state file
        :param state: the state as an str, an dict or an list of states or None for default
        :param models: the models to use in this case
        """
        model_copy = list(models)
        for i, model in enumerate(models):
            if isinstance(model, BlockModel):
                model_copy[i] = ModelRepr.for_model(model)
            elif type(model) == str:
                model_copy[i] = ModelRepr(model)
        self.states.append((state, tuple(model_copy)))
        return self

    def addAliasName(self, name: str, target: str):
        self.alias[name] = target
        return self

    def generateBestAlias(self, limit=2):
        """
        Helper function for generating aliases where possible
        :param limit: when an model alias should be created
        """
        model_counter = {}
        for state, models in self.states:
            for model in models:
                model_counter.setdefault(model.model, [0, []])
                model_counter[model.model][0] += 1
                model_counter[model.model][1].append(model)
        i = 0
        for name in model_counter:
            if name in self.alias or name.startswith("alias:"):
                continue
            if model_counter[name][0] >= limit:
                alias_name = "alias:{}".format(i)
                self.addAliasName(alias_name, name)
                i += 1
                for model in model_counter[name][1]:
                    model.model = alias_name
        return self

    def dump(self, generator: DataGeneratorInstance) -> dict:
        if self.generate_alias > 0:
            self.generateBestAlias(self.generate_alias)
        data = {"variants": {}}
        for key, model in self.states:
            m = (
                model[0].dump(generator)
                if len(model) == 1
                else [e.dump(generator) for e in model]
            )
            if type(key) == list:
                for key2 in key:
                    data["variants"][encode_model_key(key2)] = m
            else:
                data["variants"][encode_model_key(key)] = m

        if self.parent is not None:
            data["parent"] = self.parent
        if len(self.alias) > 0:
            data["alias"] = self.alias

        return data

    def get_default_location(self, generator: DataGeneratorInstance, name: str):
        return (
            "assets/{}/blockstates/{}.json".format(*name.split(":"))
            if ":" in name
            else "assets/{}/blockstates/{}.json".format(
                generator.default_namespace, name
            )
        )


class MultiPartBlockState(IDataGenerator):
    """
    Generator class for an multipart model
    """

    def __init__(self, name: str, parent=None, optimize=True):
        self.name = name
        self.states = []
        self.parent = parent
        self.alias = {}
        self.optimize = optimize

    def add_state(self, state: typing.Union[None, str, dict, list], *models):
        """
        will add an entry
        :param state: the case in which this should be active.
            None: always
            str: represents an list of "<name>=<state>" separated by "," as state
            dict: represents same as str, but not packed
            list: represents an OR over an list of state-like-entries
        :param models: the models to apply
        :return:
        """
        model_copy = list(models)
        for i, model in enumerate(models):
            if type(model) == str:
                model_copy[i] = ModelRepr(model)
        self.states.append((state, model_copy))
        return self

    def addAliasName(self, name: str, target: str):
        self.alias[name] = target
        return self

    def generateBestAlias(self, limit=2):
        """
        Helper function for generating aliases where possible
        :param limit: when an model alias should be created
        """
        model_counter = {}
        for state, models in self.states:
            for model in models:
                model_counter.setdefault(model.model, [0, []])
                model_counter[model.model][0] += 1
                model_counter[model.model][1].append(model)
        i = 0
        for name in model_counter:
            if name in self.alias or name.startswith("alias:"):
                continue
            if model_counter[name][0] >= limit:
                alias_name = "alias:{}".format(i)
                self.addAliasName(alias_name, name)
                i += 1
                for model in model_counter[name][1]:
                    model.model = alias_name
        return self

    def dump(self, generator: DataGeneratorInstance) -> dict:
        if self.optimize:
            self.generateBestAlias()
        data = {"multipart": []}
        if self.parent is not None:
            data["parent"] = self.parent
        if len(self.alias) > 0:
            data["alias"] = self.alias
        for state, model in self.states:
            m = (
                model[0].dump(generator)
                if len(model) == 1
                else [e.dump(generator) for e in model]
            )
            d = {"apply": m}
            c = self._encode_condition(state)
            if c is not None:
                d["when"] = c
            data["multipart"].append(d)

        return data

    @classmethod
    def _encode_condition(cls, state):
        if state is not None:
            if type(state) == str:
                state = {e.split("=")[0]: e.split("=")[1] for e in state.split(",")}
            if type(state) == dict:
                return state
            if type(state) == list:
                return {"OR": [cls._encode_condition(e) for e in state]}
            raise NotImplementedError()

    def get_default_location(self, generator: DataGeneratorInstance, name: str):
        return (
            "assets/{}/blockstates/{}.json".format(*name.split(":"))
            if ":" in name
            else "assets/{}/blockstates/{}.json".format(
                generator.default_namespace, name
            )
        )


class ModelDisplay(IDataGenerator):
    """
    class holding an display configuration for the block
    """

    def __init__(
        self, rotation: tuple = None, translation: tuple = None, scale: tuple = None
    ):
        """
        creates an new config for an display
        :param rotation: the rotation to use
        :param translation: the translation to use
        :param scale: the scale to use
        """
        self.rotation = rotation
        self.translation = translation
        self.scale = scale

    def dump(self, generator: DataGeneratorInstance) -> dict:
        data = {}
        if self.rotation is not None:
            data["rotation"] = self.rotation
        if self.translation is not None:
            data["translation"] = self.translation
        if self.scale is not None:
            data["scale"] = self.scale
        return data


class BlockModel(IDataGenerator):
    """
    Generator for a block model
    """

    def __init__(
        self,
        name: str,
        parent: str = "minecraft:block/block",
        ambient_occlusion=True,
    ):
        self.name = name
        self.parent = parent
        self.ambient_occlusion = ambient_occlusion
        self.textures = {}
        self.elements = []
        self.display = {}

    def set_texture_variable(self, name: str, texture: str):
        self.textures[name] = texture
        return self

    def set_texture_variables(self, texture: str, *names):
        [self.set_texture_variable(name, texture) for name in names]
        return self

    def add_element(
        self,
        f: tuple,
        t: tuple,
        *faces,
        rotation_center=None,
        rotation_axis=None,
        rotation_angle=None,
        rotation_rescale=False,
        shade=True
    ):
        assert len(faces) == 6, "faces must be 6"
        self.elements.append(
            (
                f,
                t,
                faces,
                rotation_center,
                rotation_axis,
                rotation_angle,
                rotation_rescale,
                shade,
            )
        )

    def set_display_mode(self, key: str, config: ModelDisplay):
        self.display[key] = config

    def dump(self, generator: DataGeneratorInstance) -> dict:
        if self.parent != "minecraft:block/block" and self.elements:
            logger.println(
                "[DATA GEN][WARN] block model {} has unusual parent and elements set".format(
                    self.name
                )
            )
        data = {"parent": self.parent}
        if not self.ambient_occlusion:
            data["ambientocclusion"] = self.ambient_occlusion
        if len(self.display) > 0:
            data["display"] = {}
            for key in self.display:
                data["display"][key] = self.display[key].dump(generator)
        if len(self.textures) > 0:
            data["textures"] = self.textures.copy()
        if len(self.elements) > 0:
            data["elements"] = []
            for (
                f,
                t,
                faces,
                rotation_center,
                rotation_axis,
                rotation_angle,
                rotation_rescale,
                shade,
            ) in self.elements:
                d = {
                    "from": f,
                    "to": t,
                    "faces": {
                        config.face.normal_name: config.dump(generator)
                        for config in faces
                    },
                }
                if any((rotation_center, rotation_angle, rotation_axis)):
                    d["rotation"] = {"origin": rotation_center, "angle": rotation_angle}
                    if rotation_rescale:
                        d["rotation"]["rescale"] = rotation_rescale
                if not shade:
                    d["shade"] = shade
                data["elements"].append(d)

        return data

    def get_default_location(self, generator: DataGeneratorInstance, name: str):
        return (
            "assets/{}/models/block/{}.json".format(*name.split(":"))
            if ":" in name
            else "assets/{}/models/block/{}.json".format(
                generator.default_namespace, name
            )
        )
