"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import texture.atlas as atlas
import texture.helpers as texturehelper
import ResourceLocator
import zipfile
import json
import time
from toposort import toposort, toposort_flatten
import util.math
import pyglet
import traceback
import os


class DrawableBox:
    """
    class for drawing boxes
    """
    def __init__(self, model, f, t, textureindex, facedata):
        self.model = model
        self.f = f
        self.t = t
        self.textureindex = textureindex
        self.boxsize = (t[0]-f[0], t[1]-f[1], t[2]-f[2])
        self.boxrposition = f
        self.facedata = facedata

    def copy(self, model, extra_texture_index={}, extra_face_data={}):
        box = DrawableBox(model, self.f, self.t, {**self.textureindex, **extra_texture_index},
                          {**self.facedata, **extra_face_data})
        return box

    def add_to_batch(self, batch, position):
        if not self.model.is_drawable:
            raise ValueError("can't draw an undrawable texture")
        x, y, z = position
        x += self.boxrposition[0] / 32
        y += self.boxrposition[1] / 32
        z += self.boxrposition[2] / 32
        textures = [None, None, None, None, None, None]
        any_texture = None
        for facename in self.facedata.keys():
            face = self.facedata[facename]
            if facename == "up":
                textures[0] = self.transform_to_texture_name(face["texture"])
            elif facename == "down":
                textures[1] = self.transform_to_texture_name(face["texture"])
            elif facename == "north":
                textures[2] = self.transform_to_texture_name(face["texture"])
            elif facename == "east":
                textures[3] = self.transform_to_texture_name(face["texture"])
            elif facename == "south":
                textures[4] = self.transform_to_texture_name(face["texture"])
            elif facename == "west":
                textures[5] = self.transform_to_texture_name(face["texture"])
            else:
                raise ValueError("can't cast face named "+str(facename)+" to valid entry")
        for texture in textures:
            if texture: any_texture = texture
        vertex = util.math.cube_vertices_2(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32,
                                           self.boxsize[2] / 32) if not (
                self.boxsize[0] == self.boxsize[1] == self.boxsize[2]) else util.math.cube_vertices(x, y, z,
                                                                                                    self.boxsize[0] /
                                                                                                    32)
        # vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32)
        return batch.add(24, pyglet.gl.GL_QUADS, atlas.generator.texture_groups[
            any_texture.get_texture_atlas_and_index()[0]],
                       ('v3f/static', vertex),
                       ('t2f/static', util.math.tex_coords_2(
                           *[textureatlasentry.get_texture_atlas_and_index()[1] if textureatlasentry else None
                             for textureatlasentry in textures]
                       )))

    def transform_to_texture_name(self, index):
        if not index.startswith("#"):
            return self.textureindex[index]
        if index[1:] in self.textureindex:
            return self.textureindex[index[1:]]
        else:
            m = self.model
            while m:
                m = m.parent
                if m:
                    model: Model = self.model.parent
                    for entry in model.data["textures"].keys():
                        overwrite = None
                        if entry == index:
                            overwrite = entry[index]
                        elif entry == index[1:]:
                            overwrite = model.data["textures"][index[1:]]
                        if overwrite:
                            if overwrite in self.textureindex:
                                return self.textureindex[overwrite]
                            elif overwrite[1:] in self.textureindex:
                                return self.textureindex[overwrite[1:]]
                            index = overwrite
            print(index, self.model.data, self.model.name)
            raise ValueError("can't cast entry "+str(index)+" to valid texture file")


class Model:
    def __init__(self, data):
        self.data = data
        self.name = None
        self.parent: Model = None
        if "parent" in data:
            if data["parent"] not in loader.loaded_models:
                loader._load_model("assets/minecraft/models/block/{}.json".format(data["parent"].split("/")[-1]))
            self.parent = loader.loaded_models[data["parent"]]
        self.textures = data["textures"] if "textures" in data else {}
        self.textureindex = {}
        self.is_drawable = True
        t = []
        for texture in self.textures.keys():
            if self.textures[texture].startswith("#"):
                self.is_drawable = False
            else:
                t.append(texture)
        self.raw_texture = [self.textures[key] for key in t]
        if self.parent:
            self.raw_texture += self.parent.raw_texture
        if self.is_drawable:
            indexes = atlas.generator.add_files_or_images(self.raw_texture)
            for i, key in enumerate(t):
                self.textureindex[key] = indexes[i]
        # load the box info
        self.boxinfo = []
        if "elements" in data:
            for element in data["elements"]:
                self.boxinfo.append(DrawableBox(self, element["from"], element["to"], self.textureindex,
                                                element["faces"]))
        if self.parent:
            for boxinfo in self.parent.boxinfo:
                self.boxinfo.append(boxinfo.copy(self, extra_texture_index=self.textureindex))


class ModelLoader:
    def __init__(self):
        self.models = {}
        self.loaded_models = {}

    def add_from_location(self, location):
        res = ResourceLocator.ResourceLocator(location)
        res.data: bytes
        encoded = res.data.decode("UTF-8")
        data = json.loads(encoded)
        # search data for dependencies, add to local list
        depend = None if "parent" not in data else data["parent"]
        self.models[location] = set([depend]) if depend else set([])

    def build(self):
        ordered = list(toposort_flatten(self.models))
        print()
        for i, entry in enumerate(ordered):
            print("\r", end="")
            print("loading model " + str(entry) + " ({}/{})".format(i+1, len(ordered)) + "" * 10, end="")
            self._load_model(entry)
        print()

    def _load_model(self, entry: str):
        if "block/"+entry.split("/")[-1].split(".")[0] in self.loaded_models:
            return
        if not entry.endswith(".json"):
            return
        res = ResourceLocator.ResourceLocator(entry)
        res.data: bytes
        encoded = res.data.decode("UTF-8")
        data = json.loads(encoded)
        model = Model(data)
        model.name = "block/"+entry.split("/")[-1].split(".")[0]
        self.loaded_models[model.name] = model

    def from_data(self, name, data):
        model = Model(data)
        model.name = name
        self.loaded_models[name] = model

    def search_in_main_jar(self):
        names = G.jar_archive.namelist()
        result = []
        print("-seaching for block definitions")
        for name in names:
            if name.endswith(".json") and name.startswith("assets/minecraft/models/block/"):
                filename = name.split("/")[-1]
                if not os.path.exists(G.local+"/assets/models/block_modified/"+filename):
                    result.append(name)
                else:
                    result.append(G.local+"/assets/models/block_modified/"+filename)
        print("-adding them")
        for i, r in enumerate(result):
            print("{}/{}".format(i+1, len(result)), end="")
            self.add_from_location(r)
            print("\r", end="")

    def show_block(self, batch, position, name) -> list:
        # name = "missing_texture"
        try:
            return self._show_block(batch, position, name)
        except:
            traceback.print_exc()
            return self._show_block(batch, position, "missing_texture")

    def _show_block(self, batch, position, name) -> list:
        if name not in self.loaded_models:
            name = "missing_texture"
        model = self.loaded_models[name]
        data = []
        for box in model.boxinfo:
            data.append(box.add_to_batch(batch, position))
        return data


loader = G.modelloader = ModelLoader()

