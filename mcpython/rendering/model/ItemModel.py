"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.rendering.BatchHelper
import mcpython.rendering.BoxModel
import mcpython.ResourceLocator
import mcpython.item.ItemAtlas
from mcpython import globals as G, logger


class IItemModelLoader:
    @classmethod
    def validate(cls, data: dict) -> bool:
        raise NotImplementedError()

    @classmethod
    def decode(cls, data: dict, model: "ItemModel"):
        raise NotImplementedError()


class DefaultLoader(IItemModelLoader):
    @classmethod
    def validate(cls, data: dict) -> bool:
        return "mod_maker" not in data

    @classmethod
    def decode(cls, data: dict, model: "ItemModel"):
        if "parent" in data:
            parent = data["parent"]
            if parent == "builtin/entity":
                pass  # todo: add missing texture OR todo: implement entity rendeirng
            elif parent == "item/generated":
                pass
            else:
                model.addParent(parent)
        if "display" in data:
            for name in data["display"]:
                e = data["display"][name]
                model.addDisplayTransform(name, e.setdefault("rotation", (0, 0, 0)), e.setdefault("translation", (0, 0, 0)), e.setdefault("scale", (1, 1, 1)))
        texture_variables = {}
        if "textures" in data:
            for name in data["textures"]:
                if name.startswith("layer"):
                    model.addTextureLayer(int(name.split("layer")[-1]), data["textures"][name])
                else:
                    texture_variables[name] = data["textures"][name]
        if "gui_light" in data:
            model.lighting = data["gui_light"]
        if "elements" in data:
            print("[FATAL] failed to decode elements tag!")
        if "overrides" in data:
            for case in data["overrides"]:
                model.addOverride(case["predicate"], case["model"])


LOADERS = [DefaultLoader]


class ItemModel:
    @classmethod
    def from_file(cls, file: str, item: str):
        data = mcpython.ResourceLocator.read(file, "json")
        model = cls(item)
        for loader in LOADERS:
            if loader.validate(data):
                loader.decode(data, model)
        return model

    def __init__(self, item: str):
        self.item = item
        self.parents = []
        self.lighting = "front"
        self.displays = {}
        self.layers = []
        self.overrides = []

    def addParent(self, parent: str):
        self.parents.append(parent)
        return self

    def addDisplayTransform(self, name: str, rotation=(0, 0, 0), translation=(0, 0, 0), scale=(1, 1, 1)):
        self.displays[name] = (rotation, translation, scale)
        return self

    def addTextureLayer(self, number: int, file: str):
        if number >= len(self.layers): self.layers += [None] * (number - len(self.layers) + 1)
        self.layers[number] = file
        return self

    def addOverride(self, predicate, replacement: str):
        self.overrides.append((predicate, replacement))
        return self

    def bake(self, helper: "ItemModelHandler"):
        for texture in self.layers:
            if texture is None: continue
            helper.atlas.schedule_item_file(texture)

    def add_to_batch(self, position: tuple, batch, context: str, state: dict) -> mcpython.rendering.BatchHelper.BatchReference:
        pass

    def draw(self, position: tuple, context: str, state: dict):
        rot, pos, scale = ((0, 0, 0), (0, 0, 0), (1, 1, 1)) if context not in self.displays else self.displays[context]
        for layer in self.layers:
            handler.atlas.get_texture_info(layer).blit(*position)


class ItemModelHandler:
    def __init__(self):
        self.models = {}
        self.atlas = mcpython.item.ItemAtlas.ItemAtlasHandler(folder=G.build+"/tmp_items")
        G.modloader("minecraft", "stage:model:item:bake")(self.bake)

    @staticmethod
    @G.modloader("minecraft", "stage:model:item:search")
    def load():
        handler.from_folder("assets/minecraft/models/item", "minecraft")

    def from_folder(self, folder: str, modname: str):
        for file in mcpython.ResourceLocator.get_all_entries(folder):
            if file.endswith("/"): continue
            item = "{}:{}".format(modname, file.split("/")[-1].split(".")[0])
            self.models[item] = ItemModel.from_file(file, item)

    def bake(self):
        G.eventhandler.call("item:bake:pre", self)
        self.atlas.load()
        for model in self.models.values():
            try:
                model.bake(self)
            except:
                logger.print_exception("error during baking item model for '{}'".format(model.item))
        self.atlas.build()
        self.atlas.dump()
        G.eventhandler.call("item:bake:post", self)

    def add_to_batch(self, itemname, *args, **kwargs) -> mcpython.rendering.BatchHelper.BatchReference:
        return self.models[itemname].add_to_batch(*args, **kwargs)

    def draw(self, itemname, *args, **kwargs):
        self.models[itemname].draw(*args, **kwargs)


handler = ItemModelHandler()
