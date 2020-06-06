"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.rendering.model.BlockState
import globals as G
import mcpython.util.enums


class BlockModelFactory:
    def __init__(self):
        self.name = None
        self.parent = "block/block"
        self.elements = None
        self.textures = None

    def setName(self, name: str):
        self.name = name
        return self

    def setParent(self, parent: str):
        self.parent = parent
        return self

    def addElement(self, f: tuple, t: tuple, textures: list, rotation=None, uvs=[(0, 0, 1, 1)]*6, texture_rotation=[0]*6):
        """
        will add an visual element to the model
        :param f: coords where to start
        :param t: coords where to end
        :param textures: the textures to use for each face, in order of util.enums.EnumSide.iterate()
        :param rotation: the rotation to use, as (<origin>, <axis>, <angle>, [<rescale>])
        :param uvs: the uv regions for the textures
        :param texture_rotation: the rotation for each texture
        """
        if self.elements is None:
            self.elements = []
        self.elements.append((f, t, textures, rotation, uvs, texture_rotation))
        return self

    def setTexture(self, key: str, texture: str):
        if self.textures is None: self.textures = {}
        self.textures[key] = texture
        return self

    def finish(self):
        assert self.name is not None
        G.modloader(self.name.split(":")[0], "stage:modelfactory:bake")(self.finish_up)

    def finish_up(self):
        assert self.name is not None
        data = {"parent": self.parent}
        if self.textures is not None:
            data["textures"] = self.textures
        if self.elements is not None:
            data["elements"] = []
            for f, t, textures, rotation, uvs, texture_rotation in self.elements:
                d = {"from": f, "to": t}
                if rotation is not None:
                    d["rotation"] = {"origin": rotation[0], "axis": rotation[1], "angle": rotation[2]}
                    if len(rotation) > 3:
                        d["rotation"]["rescale"] = rotation[3]
                for i, face in enumerate(mcpython.util.enums.EnumSide.iterate()):
                    e = {"texture": textures[i]}
                    if uvs is not None: e["uv"] = uvs[i]
                    if texture_rotation is not None: e["rotation"] = texture_rotation[i]
                    d["faces"][face.normal_name] = e
                data["elements"].append(d)
        G.modloader(self.name.split(":")[0], "stage:model:model_search",
                    lambda: G.modelhandler.add_from_data(self.name, data))


class NormalBlockStateFactory:
    def __init__(self):
        self.name = None
        self.variants = []

    def setName(self, name: str):
        self.name = name
        return self

    def addVariant(self, variant_descriptor: str, *models):
        self.variants.append((variant_descriptor, models))
        return self

    def finish(self):
        assert self.name is not None
        G.modloader(self.name.split(":")[0], "stage:blockstatefactory:bake")(self.finish_up)

    def finish_up(self):
        assert self.name is not None
        data = {"variants": {}}
        for key, value in self.variants:
            d = []
            for e in value:
                d.append({"model": e} if type(e) == str else e)
            data["variants"][key] = d
        G.modloader(self.name.split(":")[0], "stage:model:blockstate_search")(
            mcpython.rendering.model.BlockState.BlockStateDefinition.from_data(self.name, data))

# todo: add factory for multipart models
