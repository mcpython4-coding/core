"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

import util.math
import util.enums
import pyglet
import block.BlockConfig


class BoxModel:
    def __init__(self, data: dict, model):
        self.data = data
        self.model = model
        self.boxposition = data["from"]
        self.boxsize = (data["to"][0] - data["from"][0], data["to"][1] - data["from"][1],
                        data["to"][2] - data["from"][2])
        self.faces = {util.enums.EnumSide.U: None, util.enums.EnumSide.D: None,
                      util.enums.EnumSide.N: None, util.enums.EnumSide.E: None,
                      util.enums.EnumSide.S: None, util.enums.EnumSide.W: None}
        for facename in util.enums.NAMED_SIDES.keys():
            if facename in data["faces"]:
                addr = data["faces"][facename]["texture"]
                self.faces[util.enums.NAMED_SIDES[facename]] = model.get_texture_position(addr)

    def add_to_batch(self, position, batch, rotation):
        x, y, z = position
        x += self.boxposition[0]
        y += self.boxposition[1]
        z += self.boxposition[2]
        up, down, north, east, south, west = tuple([self.faces[x] for x in util.enums.SIDE_ORDER])
        indexes = [0] * 6
        if any(rotation):
            # print(rotation)
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
                                         south[indexes[4]], west[indexes[4]], size=self.model.texture_atlas.size)
        result = []
        vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                         [True] * 6)
        batch = batch[0] if self.model.name not in block.BlockConfig.ENTRYS["alpha"] else batch[1]
        for i in range(6):
            t = rtextures[i * 8:i * 8 + 8]
            result.append(batch.add(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group,
                                       ('v3f/static', vertex[i * 12:i * 12 + 12]),
                                       ('t2f/static', t)))
        return result

    def copy(self, new_model=None):
        return BoxModel(self.data, new_model if new_model else self.model)

