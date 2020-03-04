"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import util.math
import util.enums
import pyglet
import block.BlockConfig
import config


UV_ORDER = ["up", "down", "north", "east", "south", "west"]
UV_INDICES = [(1, 0, 3, 2), (1, 0, 3, 2)] + [(0, 1, 2, 3)] * 4   # representative for the order of uv insertion


class BoxModel:
    def __init__(self, data: dict, model):
        self.data = data
        self.model = model
        self.boxposition = [x / 16 for x in data["from"]]
        self.boxsize = (data["to"][0] - data["from"][0], data["to"][1] - data["from"][1],
                        data["to"][2] - data["from"][2])
        self.rposition = [x // 2 / 16 for x in self.boxsize]
        self.faces = {util.enums.EnumSide.U: None, util.enums.EnumSide.D: None,
                      util.enums.EnumSide.N: None, util.enums.EnumSide.E: None,
                      util.enums.EnumSide.S: None, util.enums.EnumSide.W: None}
        UD = (data["from"][0] / 16, data["from"][2] / 16, data["to"][0] / 16, data["to"][2] / 16)
        NS = (data["from"][0] / 16, data["from"][1] / 16, data["to"][0] / 16, data["to"][1] / 16)
        EW = (data["from"][2] / 16, data["from"][1] / 16, data["to"][2] / 16, data["to"][1] / 16)
        self.texregion = [UD, UD, NS, EW, NS, EW]
        for face in util.enums.EnumSide.iterate():
            facename = face.normal_name
            if facename in data["faces"]:
                addr = data["faces"][facename]["texture"]
                self.faces[util.enums.EnumSide[facename.upper()]] = model.get_texture_position(addr)
                if "uv" in data["faces"][facename]:
                    uvs = tuple(data["faces"][facename]["uv"])
                    index = UV_ORDER.index(facename)
                    self.texregion[index] = tuple([uvs[i]/16 for i in UV_INDICES[index]])

    def add_to_batch(self, position, batch, rotation, active_faces=None):
        x, y, z = position
        x += self.boxposition[0] - 0.5 + self.rposition[0]
        y += self.boxposition[1] - 0.5 + self.rposition[1]
        z += self.boxposition[2] - 0.5 + self.rposition[2]
        up, down, north, east, south, west = array = tuple([self.faces[x] if self.faces[x] is not None else (0, 0)
                                                            for x in util.enums.EnumSide.iterate()])
        deactive = [x == (0, 0) or x is None for x in array]
        rtextures = util.math.tex_coords(up, down, north, east, south, west, size=self.model.texture_atlas.size,
                                         tex_region=self.texregion)
        vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                         [True] * 6)
        # todo: can we cache this -> better performance?
        vertex_r = [util.math.rotate_point(vertex[i*3:i*3+3], position, rotation) for i in range(len(vertex) // 3)]
        vertex.clear()
        for element in vertex_r: vertex.extend(element)
        batch = batch[0] if self.model.name not in block.BlockConfig.ENTRYS["alpha"] else batch[1]
        result = []
        for i in range(6):
            if active_faces is None or (active_faces[i] if type(active_faces) == list else (
                    i not in active_faces or active_faces[i])):
                if not config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE and deactive[i]: continue
                t = rtextures[i * 8:i * 8 + 8]
                v = vertex[i * 12:i * 12 + 12]
                result.append(batch.add(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group, ('v3f/static', v),
                                        ('t2f/static', t)))
        return result

    def draw(self, position, rotation, active_faces=None):
        x, y, z = position
        x += self.boxposition[0] - 0.5 + self.rposition[0]
        y += self.boxposition[1] - 0.5 + self.rposition[1]
        z += self.boxposition[2] - 0.5 + self.rposition[2]
        up, down, north, east, south, west = array = tuple([self.faces[x] if self.faces[x] is not None else (0, 0)
                                                            for x in util.enums.EnumSide.iterate()])
        deactive = [x == (0, 0) or x is None for x in array]
        rtextures = util.math.tex_coords(up, down, north, east, south, west, size=self.model.texture_atlas.size,
                                         tex_region=self.texregion)
        vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                         [True] * 6)
        # todo: can we cache this -> better performance?
        vertex_r = [util.math.rotate_point(vertex[i * 3:i * 3 + 3], position, rotation) for i in
                    range(len(vertex) // 3)]
        vertex.clear()
        for element in vertex_r: vertex.extend(element)
        for i in range(6):
            if active_faces is None or (active_faces[i] if type(active_faces) == list else (
                    i not in active_faces or active_faces[i])):
                if not config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE and deactive[i]: continue
                t = rtextures[i * 8:i * 8 + 8]
                v = vertex[i * 12:i * 12 + 12]
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group, ('v3f/static', v),
                                        ('t2f/static', t))

    def add_face_to_batch(self, position, batch, rotation, face):
        if rotation == (90, 90, 0): rotation = (0, 0, 90)
        face = face.rotate(rotation)
        return self.add_to_batch(position, batch, rotation, active_faces={i: x == face for i, x in enumerate(
            util.enums.EnumSide.iterate())})

    def draw_face(self, position, rotation, face):
        if rotation == (90, 90, 0): rotation = (0, 0, 90)
        face = face.rotate(rotation)
        return self.draw(position, rotation, active_faces={i: x == face for i, x in enumerate(
            util.enums.EnumSide.iterate())})

    def copy(self, new_model=None):
        return BoxModel(self.data, new_model if new_model is not None else self.model)

