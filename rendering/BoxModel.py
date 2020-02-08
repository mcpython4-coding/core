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
                    uvfx, uvfy, uvtx, uvty = tuple(data["faces"][facename]["uv"])
                    self.texregion[UV_ORDER.index(facename)] = (uvfx/16, 1-uvfy/16, uvtx/16, 1-uvty/16)

    def add_to_batch(self, position, batch, rotation, active_faces=None):
        # logger.println(self.faces)
        x, y, z = position
        x += self.boxposition[0] - 0.5 + self.rposition[0]
        y += self.boxposition[1] - 0.5 + self.rposition[1]
        z += self.boxposition[2] - 0.5 + self.rposition[2]
        up, down, north, east, south, west = array = tuple([self.faces[x] if self.faces[x] is not None else [(0, 0)] * 4
                                                            for x in util.enums.EnumSide.iterate()])
        deactive = [x[0] == (0, 0) or x is None for x in array]
        indexes = [0] * 6
        if any(rotation):
            # logger.println(rotation)
            if rotation[0]:  # rotate around x
                for _ in range(rotation[0] // 90):
                    east, west, up, down = up, down, east, west
                    indexes[0] += 1; indexes[0] %= 4
                    indexes[2] += 1; indexes[2] %= 4
                    indexes[3] += 1; indexes[1] %= 4
                    indexes[4] += 1; indexes[4] %= 4
            if rotation[1]:  # rotate around y
                for _ in range(rotation[1] // 90):
                    indexes[0] += 1; indexes[0] %= 4
                    indexes[1] += 1; indexes[0] %= 4
                    north, east, south, west = east, south, west, north
            if rotation[2]:  # rotate around z
                for _ in range(rotation[2] // 90):
                    indexes[3] += 1; indexes[3] %= 4
                    indexes[5] += 1; indexes[5] %= 4
                    indexes[1] += 1; indexes[1] %= 4
                    north, south, up, down = up, down, north, south
        rtextures = util.math.tex_coords(up[indexes[0]], down[indexes[1]], north[indexes[2]], east[indexes[3]],
                                         south[indexes[4]], west[indexes[4]], size=self.model.texture_atlas.size,
                                         tex_region=self.texregion)
        result = []
        vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                         [True] * 6)
        batch = batch[0] if self.model.name not in block.BlockConfig.ENTRYS["alpha"] else batch[1]
        for i in range(6):
            if active_faces is None or (active_faces[i] if type(active_faces) == list else (
                    i not in active_faces or active_faces[i])):
                if not config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE and deactive[i]: continue
                t = rtextures[i * 8:i * 8 + 8]
                v = vertex[i * 12:i * 12 + 12]
                result.append(batch.add(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group, ('v3f/static', v),
                                        ('t2f/static', t)))
        return result

    def add_face_to_batch(self, position, batch, rotation, face):
        return self.add_to_batch(position, batch, rotation, active_faces={i: x == face for i, x in enumerate(
            util.enums.EnumSide.iterate())})

    def copy(self, new_model=None):
        return BoxModel(self.data, new_model if new_model else self.model)

