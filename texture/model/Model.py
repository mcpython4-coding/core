"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import texture.TextureAtlas as textureatlas
import rendering.BoxModel


class Model:
    def __init__(self, data: dict, name: str):
        self.data = data
        self.name = name
        self.parent = data["parent"] if "parent" in data else None
        self.used_textures = {}
        self.texture_addresses = {}
        self.texturerename = {}
        if self.parent:
            if self.parent not in G.modelhandler.models:
                G.modelhandler.load_model(self.parent)
            self.parent = G.modelhandler.models[self.parent]
            self.used_textures = self.parent.used_textures.copy()
            self.texturerename = self.parent.texturerename.copy()
        self.drawable = True
        if "textures" in data:
            for name in data["textures"].keys():
                texture = data["textures"][name]
                if not texture.startswith("#"):
                    self.used_textures[name] = texture
                else:
                    self.drawable = False
                    self.texturerename[name] = texture
        toadd = []
        for name in self.used_textures: toadd.append((name, self.used_textures[name]))
        add = textureatlas.handler.add_image_files([x[1] for x in toadd])
        self.texture_atlas = None
        for i, (name, _) in enumerate(toadd):
            self.texture_addresses[name] = add[i][0]
            self.texture_atlas = add[i][1]
        self.boxmodels = [] if not self.parent else [x.copy(new_model=self) for x in self.parent.boxmodels]
        if "elements" in data:
            for element in data["elements"]:
                self.boxmodels.append(rendering.BoxModel.BoxModel(element, self))

    def add_to_batch(self, position, batch, config) -> list:
        if not self.drawable: raise NotImplementedError("can't draw an model which has not definined textures")
        data = []
        for boxmodel in self.boxmodels:
            data += boxmodel.add_to_batch(position, batch, config["rotation"])
        return data

    def get_texture_position(self, name: str) -> tuple:
        if not self.drawable: return 0, 0
        if name in self.texture_addresses: return self.texture_addresses[name]
        if name in self.texturerename: return self.get_texture_position(self.texturerename[name])
        if name.startswith("#"):
            fname = name[1:]
            if fname in self.texture_addresses: return self.texture_addresses[fname]
            if fname in self.texturerename: return self.get_texture_position(self.texturerename[fname])
        # print(name, self.used_textures, self.texturerename)


