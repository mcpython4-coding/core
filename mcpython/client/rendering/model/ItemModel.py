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
import mcpython.client.rendering.model.BoxModel
import mcpython.common.item.ItemTextureAtlas
import mcpython.engine.rendering.BatchHelper
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.client.rendering.model.api import IItemModelLoader
from mcpython.client.texture import TextureAtlas
from mcpython.engine import logger

from .BoxModel import BoxModel


class DefaultLoader(IItemModelLoader):
    @classmethod
    def validate(cls, data: dict) -> bool:
        return "mod_maker" not in data

    @classmethod
    def decode(cls, data: dict, model: "ItemModel"):
        if "parent" in data:
            parent = data["parent"]
            if parent == "builtin/entity":
                pass  # todo: add missing texture OR implement entity rendering
            elif parent == "item/generated":
                model.is_layered = True
            else:
                model.addParent(parent)

        if "display" in data:
            for name in data["display"]:
                e = data["display"][name]
                model.addDisplayTransform(
                    name,
                    e.setdefault("rotation", (0, 0, 0)),
                    e.setdefault("translation", (0, 0, 0)),
                    e.setdefault("scale", (1, 1, 1)),
                )

        textures = []

        if "textures" in data:
            for name in data["textures"]:
                if name.startswith("layer"):
                    if model.is_layered:
                        model.addTextureLayer(
                            int(name.split("layer")[-1]), data["textures"][name]
                        )
                elif data["textures"][name].startswith("#"):
                    model.texture_variables[name] = data["textures"][name]
                else:
                    textures.append((name, data["textures"][name]))

        for e, pos in zip(
            textures,
            TextureAtlas.handler.add_image_files(
                [x[1] for x in textures], model.name.split(":")[0]
            ),
        ):
            model.textures[e[0]] = pos
            model.texture_atlas = pos[1]
            model.drawable = True

        if "gui_light" in data:
            model.lighting = data["gui_light"]

        if "elements" in data:
            if model.is_layered:
                raise RuntimeError(
                    f"Layered model {model.name} cannot be child of 'item/generated' and at the same time contain elements!"
                )

            for element in data["elements"]:
                model.add_box(BoxModel().parse_mc_data(element, model))

        if "overrides" in data:
            for case in data["overrides"]:
                model.addOverride(case["predicate"], case["model"])


class ItemModel:
    LOADERS = [DefaultLoader]

    @classmethod
    def from_file(cls, file: str, item: str):
        data = mcpython.engine.ResourceLoader.read_json(file)
        return cls.from_data(data, item)

    @classmethod
    def from_data(cls, data, item):
        model = cls(item)
        for loader in cls.LOADERS:
            if loader.validate(data):
                loader.decode(data, model)
        return model

    def __init__(self, item: str):
        self.name = item
        self.parents = []
        self.lighting = "front"
        self.displays = {}
        self.layers = []
        self.overrides = []
        self.texture_variables = {}
        self.textures = {}

        self.is_layered = False
        self.drawable = False
        self.texture_atlas = None

    def __repr__(self):
        return "ItemModel(of='{}')".format(self.item)

    def addParent(self, parent: str):
        self.parents.append(parent)
        return self

    def add_box(self, box: BoxModel):
        pass

    def get_texture_position(self, name: str):
        if name in self.textures:
            return self.textures[name][0]

        if name in self.texture_variables:
            return self.get_texture_position(self.texture_variables[name])

        if name.startswith("#"):
            n = name[1:]
            if n in self.textures:
                return self.textures[n][0]

            if n in self.texture_variables:
                return self.get_texture_position(self.texture_variables[n])

        return 0, 0

    def addDisplayTransform(
        self, name: str, rotation=(0, 0, 0), translation=(0, 0, 0), scale=(1, 1, 1)
    ):
        self.displays[name] = (rotation, translation, scale)
        return self

    def addTextureLayer(self, number: int, file: str):
        if number >= len(self.layers):
            self.layers += [None] * (number - len(self.layers) + 1)
        self.layers[number] = file
        return self

    def addOverride(self, predicate, replacement: str):
        self.overrides.append((predicate, replacement))
        return self

    def bake(self, helper: "ItemModelHandler"):
        for i, texture in enumerate(self.layers):
            if texture is None:
                continue
            helper.atlas.add_file("{}#:{}".format(self.name, i), texture)

    def add_to_batch(
        self, position: tuple, batch, context: str, state: dict
    ) -> mcpython.engine.rendering.BatchHelper.BatchReference:
        pass

    def draw(self, position: tuple, context: str, state: dict):
        """rot, pos, scale = (
            ((0, 0, 0), (0, 0, 0), (1, 1, 1))
            if context not in self.displays
            else self.displays[context]
        )"""
        if self.is_layered:
            for i, layer in enumerate(self.layers):
                if layer is not None:
                    handler.atlas.get_texture_info("{}#:{}".format(self.name, i)).blit(
                        *position
                    )


class ItemModelHandler:
    def __init__(self):
        self.models = {}
        self.atlas = mcpython.common.item.ItemTextureAtlas.ItemAtlasHandler(
            folder=shared.build + "/tmp_items"
        )
        shared.mod_loader("minecraft", "stage:model:item:on_bake")(self.bake)

    @staticmethod
    @shared.mod_loader("minecraft", "stage:model:item:search")
    def load():
        handler.from_folder("assets/minecraft/models/item", "minecraft")

    def from_data(self, data: dict, name: str):
        self.models[name] = ItemModel.from_data(data, name)

    def from_folder(self, folder: str, modname: str):
        for file in mcpython.engine.ResourceLoader.get_all_entries(folder):
            if file.endswith("/"):
                continue
            item = "{}:{}".format(modname, file.split("/")[-1].split(".")[0])
            self.models[item] = ItemModel.from_file(file, item)

    def bake(self):
        self.atlas.load()
        for model in self.models.values():
            try:
                model.bake(self)
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                logger.print_exception(
                    "error during baking item model for '{}'".format(model.item)
                )

        self.atlas.build()
        self.atlas.dump()

    def add_to_batch(
        self, item_name, *args, **kwargs
    ) -> mcpython.engine.rendering.BatchHelper.BatchReference:
        return self.models[item_name].add_to_batch(*args, **kwargs)

    def draw(self, item_name, *args, **kwargs):
        self.models[item_name].draw(*args, **kwargs)


handler = ItemModelHandler()
