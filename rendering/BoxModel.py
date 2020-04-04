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
import mod.ModMcpython
import ResourceLocator


UV_ORDER = ["up", "down", "north", "east", "south", "west"]
UV_INDICES = [(1, 0, 3, 2), (1, 0, 3, 2)] + [(0, 1, 2, 3)] * 4   # representative for the order of uv insertion
SIMILAR_VERTEX = {}


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
        self.texregionrotate = [0] * 6
        for face in util.enums.EnumSide.iterate():
            facename = face.normal_name
            if facename in data["faces"]:
                f = data["faces"][facename]
                addr = f["texture"]
                self.faces[util.enums.EnumSide[facename.upper()]] = model.get_texture_position(addr)
                index = UV_ORDER.index(facename)
                if "uv" in f:
                    uvs = tuple(f["uv"])
                    self.texregion[index] = tuple([uvs[i]/16 for i in UV_INDICES[index]])
                if "rotation" in f:
                    self.texregionrotate[index] = f["rotation"]
        self.rotation = (0, 0, 0)
        self.rotation_core = (0, 0, 0)
        if "rotation" in data:
            if "origin" in data["rotation"]:
                self.rotation_core = tuple(data["rotation"]["origin"])
            rot = [0, 0, 0]
            rot["xyz".index(data["rotation"]["axis"])] = data["rotation"]["angle"]
            self.rotation = tuple(rot)

        status = (self.rotation, self.rotation_core, tuple(self.boxposition), self.boxsize)
        if status in SIMILAR_VERTEX:
            self.rotated_vertices = SIMILAR_VERTEX[status].rotated_vertices
        else:
            self.rotated_vertices = {}
            SIMILAR_VERTEX[status] = self

        self.tex_data = None
        self.deactive = None

        if model.drawable and self.model.texture_atlas:
            mod.ModMcpython.mcpython.eventbus.subscribe("stage:boxmodel:bake", self.build)

    def build(self):
        up, down, north, east, south, west = array = tuple([self.faces[x] if self.faces[x] is not None else (0, 0)
                                                            for x in util.enums.EnumSide.iterate()])
        self.tex_data = util.math.tex_coords(up, down, north, east, south, west, size=self.model.texture_atlas.size,
                                             tex_region=self.texregion, rotation=self.texregionrotate)
        self.deactive = {face: array[i] == (0, 0) or array[i] is None for i, face in enumerate(
            util.enums.EnumSide.iterate())}

    def add_to_batch(self, position, batch, rotation, active_faces=None):
        x, y, z = position
        x += self.boxposition[0] - 0.5 + self.rposition[0]
        y += self.boxposition[1] - 0.5 + self.rposition[1]
        z += self.boxposition[2] - 0.5 + self.rposition[2]
        if rotation in self.rotated_vertices:  # is there data prepared in this case?
            vertex_r = [(e[0]+x, e[1]+y, e[2]+z) for e in self.rotated_vertices[rotation]]
        else:  # otherwise, create it and store it
            vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                             [True] * 6)
            vertex_r = [util.math.rotate_point(vertex[i * 3:i * 3 + 3], position, rotation) for i in
                        range(len(vertex) // 3)]
            vertex_r = [util.math.rotate_point(e, tuple([position[i] + self.rotation_core[i] for i in range(3)]),
                                               self.rotation) for e in vertex_r]
            self.rotated_vertices[rotation] = [(e[0]-x, e[1]-y, e[2]-z) for e in vertex_r]
        vertex = []
        for element in vertex_r: vertex.extend(element)
        batch = batch[0] if self.model.name not in block.BlockConfig.ENTRYS["alpha"] else batch[1]
        result = []
        for i in range(6):
            if active_faces is None or (active_faces[i] if type(active_faces) == list else (
                    i not in active_faces or active_faces[i])):
                if not config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE and \
                        self.deactive[util.enums.EnumSide.iterate()[i].rotate(rotation)]: continue
                t = self.tex_data[i * 8:i * 8 + 8]
                v = vertex[i * 12:i * 12 + 12]
                result.append(batch.add(4, pyglet.gl.GL_QUADS, self.model.texture_atlas.group, ('v3f/static', v),
                                        ('t2f/static', t)))
        return result

    def draw(self, position, rotation, active_faces=None):
        x, y, z = position
        x += self.boxposition[0] - 0.5 + self.rposition[0]
        y += self.boxposition[1] - 0.5 + self.rposition[1]
        z += self.boxposition[2] - 0.5 + self.rposition[2]
        if rotation in self.rotated_vertices:  # is there data prepared in this case?
            vertex_r = [(e[0] + x, e[1] + y, e[2] + z) for e in self.rotated_vertices[rotation]]
        else:  # otherwise, create it and store it
            vertex = util.math.cube_vertices(x, y, z, self.boxsize[0] / 32, self.boxsize[1] / 32, self.boxsize[2] / 32,
                                             [True] * 6)
            vertex_r = [util.math.rotate_point(vertex[i * 3:i * 3 + 3], position, rotation) for i in
                        range(len(vertex) // 3)]
            vertex_r = [util.math.rotate_point(e, tuple([position[i] + self.rotation_core[i] for i in range(3)]),
                                               self.rotation) for e in vertex_r]
            self.rotated_vertices[rotation] = [(e[0] - x, e[1] - y, e[2] - z) for e in vertex_r]
        vertex = []
        for element in vertex_r: vertex.extend(element)
        for i in range(6):
            if active_faces is None or (active_faces[i] if type(active_faces) == list else (
                    i not in active_faces or active_faces[i])):
                if not config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE and \
                        self.deactive[util.enums.EnumSide.iterate()[i].rotate(rotation)]: continue
                t = self.tex_data[i * 8:i * 8 + 8]
                v = vertex[i * 12:i * 12 + 12]
                self.model.texture_atlas.group.set_state()
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v3f/static', v), ('t2f/static', t))
                self.model.texture_atlas.group.unset_state()

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


class BaseBoxModel:
    """
    an non-model-bound boxmodel class
    """

    def __init__(self, relative_position: tuple, size: tuple, texture, texture_region=[(0, 0, 1, 1)]*6,
                 rotation=(0, 0, 0), rotation_center=None):
        """
        creates an new renderer for the box-model
        :param relative_position: where to position the box relative to draw position
        :param size: the size of the box
        :param texture: which texture to use. May be str or pyglet.graphics.TextureGroup
        :param texture_region: which tex region to use, from (0, 0) to (1, 1)
        :param rotation: how to rotate the bbox
        :param rotation_center: where to rotate the box around
        """
        self.relative_position = relative_position
        self.size = size
        self.texture = texture if type(texture) == pyglet.graphics.TextureGroup else pyglet.graphics.TextureGroup(
            ResourceLocator.read(texture, "pyglet").get_texture())
        self.__texture_region = texture_region
        self.__rotation = rotation
        self.vertex_cache = []
        self.rotated_vertex_cache = {}
        self.texture_cache = None
        self.rotation_center = rotation_center if rotation_center is not None else relative_position
        self.recalculate_cache()

    def recalculate_cache(self):
        vertices = util.math.cube_vertices(*self.relative_position, *[self.size[i] / 2 for i in range(3)])
        self.vertex_cache.clear()
        for i in range(len(vertices) // 3):
            self.vertex_cache.append(util.math.rotate_point(vertices[i*3:i*3+3], self.rotation_center, self.__rotation))
        self.texture_cache = util.math.tex_coords(*[(0, 0)]*6, size=(1, 1), tex_region=self.__texture_region)

    def get_rotation(self): return self.__rotation

    def set_rotation(self, rotation: tuple):
        self.__rotation = rotation
        self.recalculate_cache()

    rotation = property(get_rotation, set_rotation)

    def get_texture_region(self): return self.__texture_region

    def set_texture_region(self, region):
        self.__texture_region = region
        self.recalculate_cache()

    texture_region = property(get_texture_region, set_texture_region)

    def add_to_batch(self, batch, position, rotation=(0, 0, 0), rotation_center=(0, 0, 0)):
        vertex = []
        x, y, z = position
        if rotation in self.rotated_vertex_cache:
            vertex = [e+position[i % 3] for i, e in enumerate(self.rotated_vertex_cache[rotation])]
        else:
            for dx, dy, dz in self.vertex_cache:
                vertex.extend(util.math.rotate_point((x+dx, y+dy, z+dz), rotation_center, rotation))
            self.rotated_vertex_cache[rotation] = vertex
        result = []
        for i in range(6):
            t = self.texture_cache[i * 8:i * 8 + 8]
            v = vertex[i * 12:i * 12 + 12]
            result.append(batch.add(4, pyglet.gl.GL_QUADS, self.texture, ('v3f/static', v), ('t2f/static', t)))

    def draw(self, position, rotation=(0, 0, 0), rotation_center=(0, 0, 0)):
        vertex = []
        x, y, z = position
        if rotation in self.rotated_vertex_cache:
            vertex = [e+position[i % 3] for i, e in enumerate(self.rotated_vertex_cache[rotation])]
        else:
            self.rotated_vertex_cache[rotation] = []
            for dx, dy, dz in self.vertex_cache:
                dx, dy, dz = util.math.rotate_point((dx, dy, dz), rotation_center, rotation)
                self.rotated_vertex_cache[rotation].extend((dx, dy, dz))
                vertex.extend((x+dx, y+dy, z+dz))
        self.texture.set_state()
        for i in range(6):
            t = self.texture_cache[i * 8:i * 8 + 8]
            v = vertex[i * 12:i * 12 + 12]
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v3f/static', v), ('t2f/static', t))
        self.texture.unset_state()

