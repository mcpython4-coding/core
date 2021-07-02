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
import typing
from abc import ABC

import mcpython.common.config
import mcpython.ResourceLoader
import mcpython.util.enums
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient
from pyglet.graphics.vertexdomain import VertexList

UV_ORDER = [
    mcpython.util.enums.EnumSide.UP,
    mcpython.util.enums.EnumSide.DOWN,
    mcpython.util.enums.EnumSide.WEST,
    mcpython.util.enums.EnumSide.EAST,
    mcpython.util.enums.EnumSide.NORTH,
    mcpython.util.enums.EnumSide.SOUTH,
]
SIDE_ORDER = [
    mcpython.util.enums.EnumSide.UP,
    mcpython.util.enums.EnumSide.DOWN,
    mcpython.util.enums.EnumSide.NORTH,
    mcpython.util.enums.EnumSide.SOUTH,
    mcpython.util.enums.EnumSide.WEST,
    mcpython.util.enums.EnumSide.EAST,
]
UV_INDICES = [(0, 3, 2, 1), (1, 0, 3, 2)] + [
    (0, 1, 2, 3)
] * 4  # representative for the order of uv insertion
SIMILAR_VERTEX = {}


class AbstractBoxModel(ABC):
    def copy(self) -> "AbstractBoxModel":
        raise NotImplementedError


@onlyInClient()
class BoxModel(AbstractBoxModel):
    @classmethod
    def new(cls, data: dict, model=None):
        return cls(data, model)

    def __init__(self, data: dict, model=None, flip_y=True):
        # todo: move most of the code here to the build function / decode function
        self.atlas = None
        self.model = model
        self.data = data

        self.box_position = tuple([x / 16 for x in data["from"]])
        self.box_size = tuple([a - b for a, b in zip(data["to"], data["from"])])

        self.relative_position = tuple([x // 2 / 16 for x in self.box_size])
        self.faces = {
            mcpython.util.enums.EnumSide.U: None,
            mcpython.util.enums.EnumSide.D: None,
            mcpython.util.enums.EnumSide.N: None,
            mcpython.util.enums.EnumSide.E: None,
            mcpython.util.enums.EnumSide.S: None,
            mcpython.util.enums.EnumSide.W: None,
        }

        UD = (
            data["from"][0] / 16,
            data["from"][2] / 16,
            data["to"][0] / 16,
            data["to"][2] / 16,
        )
        NS = (
            data["from"][0] / 16,
            data["from"][1] / 16,
            data["to"][0] / 16,
            data["to"][1] / 16,
        )
        EW = (
            data["from"][2] / 16,
            data["from"][1] / 16,
            data["to"][2] / 16,
            data["to"][1] / 16,
        )
        self.texture_region = [UD, UD, NS, EW, NS, EW]
        self.texture_region_rotate = [0] * 6

        for face in mcpython.util.enums.EnumSide.iterate():
            name: str = face.normal_name

            if name in data["faces"]:
                f = data["faces"][name]
                var = f["texture"]
                self.faces[face] = (
                    model.get_texture_position(var) if model is not None else None
                )
                index = SIDE_ORDER.index(face)

                if "uv" in f:
                    uvs = tuple(f["uv"])
                    uvs = (uvs[0], uvs[3], uvs[2], uvs[1])
                    if flip_y:
                        self.texture_region[index] = tuple(
                            [
                                (uvs[i] / 16) if i % 2 == 0 else (1 - uvs[i] / 16)
                                for i in UV_INDICES[index]
                            ]
                        )
                    else:
                        self.texture_region[index] = tuple(
                            [uvs[i] / 16 for i in UV_INDICES[index]]
                        )

                if "rotation" in f:
                    self.texture_region_rotate[index] = f["rotation"]

        self.rotation = (0, 0, 0)
        self.rotation_center = (0, 0, 0)

        if "rotation" in data:
            # Another rotation center than 0, 0, 0
            if "origin" in data["rotation"]:
                self.rotation_center = tuple(e / 16 for e in data["rotation"]["origin"])

            rot = [0, 0, 0]
            rot["xyz".index(data["rotation"]["axis"])] = data["rotation"]["angle"]
            self.rotation = tuple(rot)

        status = (
            self.rotation,
            self.rotation_center,
            tuple(self.box_position),
            self.box_size,
        )
        if status in SIMILAR_VERTEX:
            self.rotated_vertices = SIMILAR_VERTEX[status].rotated_vertices
        else:
            self.rotated_vertices = {}
            SIMILAR_VERTEX[status] = self

        self.tex_data = None
        self.inactive = None

        if model is not None and model.drawable and self.model.texture_atlas:
            self.build()

        self.raw_vertices = mcpython.util.math.cube_vertices_better(
            0,
            0,
            0,
            self.box_size[0] / 32,
            self.box_size[1] / 32,
            self.box_size[2] / 32,
            [True] * 6,
        )

    def build(self, atlas=None):
        """
        "Builds" the model by preparing internal data like preparing the texture atlas, the texture coordinates
        """

        if atlas is None:
            atlas = self.model.texture_atlas

        up, down, north, east, south, west = array = tuple(
            [
                self.faces[x] if self.faces[x] is not None else (0, 0)
                for x in mcpython.util.enums.EnumSide.iterate()
            ]
        )

        self.tex_data = mcpython.util.math.tex_coordinates_better(
            up,
            down,
            north,
            east,
            south,
            west,
            tex_region=self.texture_region,
            size=atlas.size,
            rotation=self.texture_region_rotate,
        )

        self.inactive = {
            face: array[i] == (0, 0) or array[i] is None
            for i, face in enumerate(mcpython.util.enums.EnumSide.iterate())
        }
        self.atlas = atlas
        # todo: can we upload vertices to GPU in advance and use some clever code for drawing?
        # todo: can we pre-calculated rotated variants for faster draw times later down the road

    def get_vertex_variant(self, rotation: tuple, position: tuple) -> list:
        """
        Implementation to get the vertex data for a rotated block
        :param rotation: the rotation to use
        :param position: the position of the vertex cube
        """
        x, y, z = (
            self.box_position[i] - 0.5 + self.relative_position[i] + position[i]
            for i in range(3)
        )

        # Is there data prepared in this case?
        if rotation in self.rotated_vertices:
            vertex_r = [
                [(e[0] + x, e[1] + y, e[2] + z) for e in m]
                for m in self.rotated_vertices[rotation]
            ]

        # Otherwise, create it and store it
        # todo: share across similar BoxModels
        else:
            vertex = mcpython.util.math.cube_vertices_better(
                x,
                y,
                z,
                self.box_size[0] / 32,
                self.box_size[1] / 32,
                self.box_size[2] / 32,
                [True] * 6,
            )

            vertex_r = []
            for face in vertex:
                face_r = []
                for i in range(len(face) // 3):
                    v = mcpython.util.math.rotate_point(
                        face[i * 3 : i * 3 + 3], position, rotation
                    )
                    v = mcpython.util.math.rotate_point(
                        v,
                        tuple(
                            [position[i] + self.rotation_center[i] for i in range(3)]
                        ),
                        self.rotation,
                    )
                    face_r.append(v)
                vertex_r.append(face_r)

            self.rotated_vertices[rotation] = [
                [(e[0] - x, e[1] - y, e[2] - z) for e in m] for m in vertex_r
            ]

        return [sum(e, tuple()) for e in vertex_r]

    def get_prepared_box_data(
        self, position, rotation, active_faces=None, uv_lock=False, previous=None
    ):
        vertex = self.get_vertex_variant(rotation, position)
        collected_data = ([], []) if previous is None else previous
        for face in mcpython.util.enums.EnumSide.iterate():
            if uv_lock:
                face = face.rotate(rotation)
            i = UV_ORDER.index(face)
            i2 = SIDE_ORDER.index(face)

            if (
                active_faces is None
                or (
                    active_faces == face.rotate(rotation)
                    if hasattr(face, "rotate")
                    else False
                )
                or (
                    (
                        active_faces[i]
                        if type(active_faces) == list
                        else (i in active_faces and active_faces[i])
                    )
                    if type(face) in (list, dict, set, tuple)
                    else False
                )
            ):
                if (
                    not mcpython.common.config.USE_MISSING_TEXTURES_ON_MISS_TEXTURE
                    and self.inactive[face.rotate(rotation)]
                ):
                    continue

                collected_data[0].extend(vertex[i])
                collected_data[1].extend(self.tex_data[i2])

        return collected_data

    def add_prepared_data_to_batch(
        self,
        collected_data: typing.Tuple[typing.List[float], typing.List[float]],
        batch: typing.Union[pyglet.graphics.Batch, typing.List[pyglet.graphics.Batch]],
    ) -> typing.Iterable[VertexList]:
        # Here we have nothing to do
        if len(collected_data[0]) == 0:
            return tuple()

        # select a batch when multiple are provided
        if type(batch) == list:
            batch = (
                batch[0]
                if self.model is not None
                and not shared.tag_handler.has_entry_tag(
                    self.model.name, "rendering", "#minecraft:alpha"
                )
                else batch[1]
            )

        # pyglet-2 thing: shader here
        # todo: export to somewhere where it is easier to exchange
        # todo: add option to make mutable
        return (
            batch.add(
                len(collected_data[0]) // 3,
                pyglet.gl.GL_QUADS,
                self.atlas.group,
                ("v3d/static", collected_data[0]),
                ("t2f/static", collected_data[1]),
            ),
        )

    def add_to_batch(
        self,
        position: typing.Tuple[float, float, float],
        batch: typing.Union[pyglet.graphics.Batch, typing.List[pyglet.graphics.Batch]],
        rotation: typing.Tuple[float, float, float],
        active_faces=None,
        uv_lock=False,
    ):
        """
        Adds the box model to the batch

        Internally wraps a get_prepared_box_data call around the add_prepared_data_to_batch method

        Use combined data where possible
        :param position: the position based on
        :param batch: the batches to select from
        :param rotation: the rotation to use
        :param active_faces: which faces to show
        :param uv_lock: if the uv's should be locked in place or not
        :return: an vertex-list-list
        todo: make active_faces an dict of faces -> state, not an order-defined list
        """
        collected_data = self.get_prepared_box_data(
            position, rotation, active_faces=active_faces, uv_lock=uv_lock
        )
        return self.add_prepared_data_to_batch(collected_data, batch)

    def draw_prepared_data(
        self, collected_data: typing.Tuple[typing.List[float], typing.List[float]]
    ):
        """
        Draws prepared data to the screen
        WARNING: the invoker is required to set up OpenGL for rendering the stuff, including linking the textures

        Use batches when possible
        :param collected_data: the data
        """
        if len(collected_data[0]) != 0:
            self.atlas.group.set_state()
            pyglet.graphics.draw(
                len(collected_data[0]) // 3,
                pyglet.gl.GL_QUADS,
                ("v3f/static", collected_data[0]),
                ("t2f/static", collected_data[1]),
            )
            self.model.texture_atlas.group.unset_state()

    def draw(
        self,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
        active_faces: typing.List[bool] = None,
        uv_lock: bool = False,
    ):
        """
        Draws the BoxModel direct into the world
        WARNING: use batches for better performance
        :param position: the position to draw on
        :param rotation: the rotation to draw with
        :param uv_lock: if the uv's should be locked in place or not
        :param active_faces: which faces to draw
        """
        collected_data = self.get_prepared_box_data(
            position, rotation, active_faces=active_faces, uv_lock=uv_lock
        )
        self.draw_prepared_data(collected_data)

    def add_face_to_batch(self, position, batch, rotation, face, uv_lock=False):
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)
        face = face.rotate(rotation)
        return self.add_to_batch(
            position,
            batch,
            rotation,
            active_faces=face,
            uv_lock=uv_lock,
        )

    def draw_face(self, position, rotation, face, uv_lock=False):
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)
        face = face.rotate(rotation)
        return self.draw(
            position,
            rotation,
            active_faces=face,
            uv_lock=uv_lock,
        )

    def copy(self, new_model=None):
        return BoxModel(self.data, new_model if new_model is not None else self.model)


@onlyInClient()
class RawBoxModel(AbstractBoxModel):
    """
    A non-model-bound BoxModel class
    """

    def __init__(
        self,
        relative_position: typing.Tuple[float, float, float],
        size: typing.Tuple[float, float, float],
        texture: typing.Union[str, pyglet.graphics.TextureGroup],
        texture_region: typing.List[typing.Tuple[float, float, float, float]] = None,
        rotation: typing.Tuple[float, float, float] = (0, 0, 0),
        rotation_center: typing.Tuple[float, float, float] = None,
    ):
        """
        Creates a new renderer for the box-model
        :param relative_position: where to draw the box, used in calculations of vertex coordinates
        :param size: the size of the box
        :param texture: which texture to use. May be str or pyglet.graphics.TextureGroup
        :param texture_region: which tex region to use, from (0, 0) to (1, 1)
        :param rotation: how to rotate the box around rotation_center
        :param rotation_center: where to rotate the box around
        """
        # default texture region is all texture
        if texture_region is None:
            texture_region = [(0, 0, 1, 1)] * 6

        self.relative_position = relative_position
        self.size = size
        self.raw_texture = texture if type(texture) == str else None

        self.texture = (
            texture
            if type(texture) == pyglet.graphics.TextureGroup
            else pyglet.graphics.TextureGroup(
                mcpython.ResourceLoader.read_pyglet_image(texture).get_texture()
            )
        )

        self.__texture_region = texture_region
        self.__rotation = rotation
        self.vertex_cache = []
        self.rotated_vertex_cache = {}
        self.texture_cache = None
        self.rotation_center = (
            rotation_center if rotation_center is not None else relative_position
        )
        self.recalculate_cache()

    def auto_value_region(
        self,
        texture_start: typing.Tuple[float, float],
        texture_dimensions: typing.Tuple[float, float, float],
    ):
        """
        Helper function for calculating the texture region in the default layout
        :param texture_start: the top left coordinates of the texture
        :param texture_dimensions: how big the texture is
        """
        x, y = texture_start
        dx, dy, dz = texture_dimensions
        self.texture_region = [
            (x + dx + dy, 1 - (dx + y), dx + dz + dy + x, 1 - y),
            (x + dx + dy + dz, 1 - (dx + y), 1 - dx + dz * 2 + dy, 1 - y),
        ] + [(0, 0, 1, 1)] * 4
        return self

    def recalculate_cache(self):
        # todo: I think we can do better here
        vertices = sum(
            mcpython.util.math.cube_vertices_better(
                *self.relative_position, *[self.size[i] / 2 for i in range(3)]
            ),
            [],
        )

        self.vertex_cache.clear()
        for i in range(len(vertices) // 3):
            self.vertex_cache.append(
                mcpython.util.math.rotate_point(
                    vertices[i * 3 : i * 3 + 3], self.rotation_center, self.__rotation
                )
            )

        # todo: this seems odd
        self.texture_cache = sum(
            mcpython.util.math.tex_coordinates_better(
                *[(0, 0)] * 6, size=(1, 1), tex_region=self.__texture_region
            ),
            tuple(),
        )

    def get_rotation(self):
        return self.__rotation

    def set_rotation(self, rotation: tuple):
        self.__rotation = rotation
        self.recalculate_cache()

    rotation = property(get_rotation, set_rotation)

    def get_texture_region(self):
        return self.__texture_region

    def set_texture_region(self, region):
        self.__texture_region = region
        self.recalculate_cache()

    texture_region = property(get_texture_region, set_texture_region)

    def get_vertices(self, position, rotation, rotation_center):
        x, y, z = position

        if rotation in self.rotated_vertex_cache:
            return [
                e + position[i % 3]
                for i, e in enumerate(self.rotated_vertex_cache[rotation])
            ]
        else:
            self.rotated_vertex_cache[rotation] = []
            vertices = []
            for dx, dy, dz in self.vertex_cache:
                dx, dy, dz = mcpython.util.math.rotate_point(
                    (dx, dy, dz), rotation_center, rotation
                )
                vertices.extend((x + dx, y + dy, z + dz))
                self.rotated_vertex_cache[rotation].extend((x, y, z))
            return vertices

    def add_to_batch(
        self, batch, position, rotation=(0, 0, 0), rotation_center=(0, 0, 0)
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        return batch.add(
            4 * 6,
            pyglet.gl.GL_QUADS,
            self.texture,
            ("v3f/static", vertices),
            ("t2f/static", self.texture_cache),
        )

    def add_face_to_batch(
        self, batch, position, face, rotation=(0, 0, 0), rotation_center=(0, 0, 0)
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        result = []
        for i in range(6):
            if not i ** 2 & face:
                continue

            t = self.texture_cache[i * 8 : i * 8 + 8]
            v = vertices[i * 12 : i * 12 + 12]
            result.append(
                batch.add(
                    4,
                    pyglet.gl.GL_QUADS,
                    self.texture,
                    ("v3f/static", v),
                    ("t2f/static", t),
                )
            )
        return result

    def draw(self, position, rotation=(0, 0, 0), rotation_center=(0, 0, 0)):
        vertices = self.get_vertices(position, rotation, rotation_center)

        if self.texture is not None:
            self.texture.set_state()

        pyglet.graphics.draw(
            4 * 6,
            pyglet.gl.GL_QUADS,
            ("v3f/static", vertices),
            ("t2f/static", self.texture_cache),
        )

        if self.texture is not None:
            self.texture.unset_state()
