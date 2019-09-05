"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

import util.math
import util.enums
import pyglet

"""
{   
    "from": [ 0, 0, 0 ],
    "to": [ 16, 16, 16 ],
    "faces": {
        "down":  { "texture": "#down", "cullface": "down" },
        "up":    { "texture": "#up", "cullface": "up" },
        "north": { "texture": "#north", "cullface": "north" },
        "south": { "texture": "#south", "cullface": "south" },
        "west":  { "texture": "#west", "cullface": "west" },
        "east":  { "texture": "#east", "cullface": "east" }
    }
}"""


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
        rtextures = util.math.tex_coords(*[self.faces[x] for x in util.enums.SIDE_ORDER])
        result = []
        vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                         [True] * 6)
        for i in range(6):
            t = rtextures[i * 8:i * 8 + 8]
            result.append(batch[0].add(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group,
                                       ('v3f/static', vertex[i * 12:i * 12 + 12]),
                                       ('t2f/static', t)))
        return result

    def copy(self, new_model=None):
        return BoxModel(self.data, new_model if new_model else self.model)
