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
import itertools
import typing

import mcpython.common.config
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.api import (
    AbstractBoxModel,
    IBlockStateRenderingTarget,
)
from mcpython.client.rendering.model.util import SIDE_ORDER, UV_INDICES, UV_ORDER
from mcpython.util.annotation import onlyInClient
from mcpython.util.enums import EnumSide
from mcpython.util.vertex import VertexProvider
from pyglet.graphics.vertexdomain import VertexList


@onlyInClient()
class BoxModel(AbstractBoxModel):
    @classmethod
    def new(cls, data: dict, model=None) -> "BoxModel":
        obj = cls()
        obj.parse_mc_data(data, model)
        return obj

    def __init__(self, flip_y=True):
        self.flip_y = flip_y

        self.vertex_provider: typing.Optional[VertexProvider] = None

        self.atlas = None
        self.model = None
        self.data = None
        self.tex_data = None
        self.inactive = None
        self.box_position = self.rotation = self.rotation_center = (0, 0, 0)
        self.box_size = 1, 1, 1

        self.faces = [None] * 6
        self.face_tint_index = [-1] * 6

        self.texture_region: typing.List[typing.Tuple[float, float, float, float]] = [
            (0, 0, 1, 1)
        ] * 6
        self.texture_region_rotate: typing.List[float] = [0] * 6

        self.enable_alpha = False

    def parse_mc_data(self, data: dict, model=None):
        """
        Parses the default "elements" tag from a vanilla model file
        :param data: one element of the "elements" tag
        :param model: the assigned model, or None if not arrival
        """

        self.model = model
        self.data = data

        self.box_position = tuple([x / 16 for x in data["from"]])
        self.box_size = tuple(
            [abs(a - b) / 16 for a, b in zip(data["to"], data["from"])]
        )

        if "rotation" in data:
            # Another rotation center than 0, 0, 0
            if "origin" in data["rotation"]:
                self.rotation_center = tuple(e / 16 for e in data["rotation"]["origin"])

            # todo: add a way to rotate around more than one axis
            rot = [0, 0, 0]
            rot["xyz".index(data["rotation"]["axis"])] = data["rotation"]["angle"]
            self.rotation = tuple(rot)

        self.vertex_provider = VertexProvider.create(
            typing.cast(
                typing.Tuple[float, float, float],
                tuple(
                    self.box_position[i] + self.box_size[i] / 2 - 0.5 for i in range(3)
                ),
            ),
            typing.cast(typing.Tuple[float, float, float], self.box_size),
            typing.cast(typing.Tuple[float, float, float], self.rotation),
        )

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
        self.texture_region[:] = [UD, UD, NS, EW, NS, EW]

        for face in mcpython.util.enums.EnumSide.iterate():
            name: str = face.normal_name

            if name in data["faces"]:
                f = data["faces"][name]
                var = f["texture"]
                self.faces[face.index] = (
                    model.get_texture_position(var) if model is not None else None
                )
                index = SIDE_ORDER.index(face)

                if "uv" in f:
                    uvs = tuple(f["uv"])
                    uvs = (uvs[0], uvs[3], uvs[2], uvs[1])
                    if self.flip_y:
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

                if "tintindex" in f:
                    self.face_tint_index[index] = f["tintindex"]

        if model is not None and model.drawable and self.model.texture_atlas:
            self.build()

        return self

    def build(self, atlas=None):
        """
        "Builds" the model by preparing internal data like preparing the texture atlas, the texture coordinates, etc.
        """

        if atlas is None:
            atlas = self.model.texture_atlas

        up, down, north, east, south, west = array = tuple(
            [self.faces[i] if self.faces[i] is not None else (0, 0) for i in range(6)]
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

        self.enable_alpha = not shared.tag_handler.has_entry_tag(
            self.model.name, "rendering", "#minecraft:alpha"
        )

        # todo: can we upload vertices to GPU in advance and use some clever code for drawing?
        # todo: can we pre-calculated rotated variants for faster draw times later down the road

    def get_vertex_variant(self, rotation: tuple, position: tuple) -> list:
        """
        Implementation to get the vertex data for a rotated block
        :param rotation: the rotation to use
        :param position: the position of the vertex cube
        """
        vertices = self.vertex_provider.get_vertex_data(position, rotation)
        return [sum(x, tuple()) for x in vertices]

    def get_prepared_box_data(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float] = (0, 0, 0),
        active_faces=None,
        uv_lock=False,
        previous: typing.Tuple[
            typing.List[float], typing.List[float], typing.List[float]
        ] = None,
    ) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Util method for getting the box data for a block (vertices and uv's)
        :param instance: the instance to get information from to render
        :param position: the position of the block
        :param rotation: the rotation
        :param active_faces: the faces to get data for, None means all
        :param uv_lock: ?
        :param previous: previous data to add the new to, or None to create new
        """
        vertex = self.get_vertex_variant(rotation, position)
        collected_data = ([], [], []) if previous is None else previous

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
                    # todo: this seems wrong
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
                collected_data[2].extend(
                    (1,) * 16
                    if self.face_tint_index[face.index] == -1
                    else instance.get_tint_for_index(self.face_tint_index[face.index])
                    * 4
                )

        return collected_data

    def add_prepared_data_to_batch(
        self,
        collected_data: typing.Tuple[
            typing.List[float], typing.List[float], typing.List[float]
        ],
        batch: typing.Union[pyglet.graphics.Batch, typing.List[pyglet.graphics.Batch]],
    ) -> typing.Iterable[VertexList]:
        """
        Adds the data from get_prepared_box_data to a given batch
        :param collected_data: the collected data
        :param batch: the batch to add in
        """
        # Here we have nothing to do
        if len(collected_data[0]) == 0:
            return tuple()

        # select a batch when multiple are provided
        if type(batch) == list:
            batch = (
                batch[0] if self.model is not None and self.enable_alpha else batch[1]
            )

        # pyglet-2 thing: shader here
        # todo: export to somewhere where it is easier to exchange

        return (
            batch.add(
                len(collected_data[0]) // 3,
                pyglet.gl.GL_QUADS,
                self.atlas.group,
                ("v3d/static", collected_data[0]),
                ("t2f/static", collected_data[1]),
                ("c4f/static", collected_data[2]),
            ),
        )

    def add_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
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
        :param instance: the instance to use for rendering
        :param position: the position based on
        :param batch: the batches to select from
        :param rotation: the rotation to use
        :param active_faces: which faces to show
        :param uv_lock: if the uv's should be locked in place or not
        :return: an vertex-list-list
        todo: make active_faces an dict of faces -> state, not an order-defined list
        """
        collected_data = self.get_prepared_box_data(
            instance, position, rotation, active_faces=active_faces, uv_lock=uv_lock
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
                ("v3d/static", collected_data[0]),
                ("t2f/static", collected_data[1]),
                ("c4f/static", collected_data[2]),
            )
            self.model.texture_atlas.group.unset_state()

    def draw(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
        active_faces: typing.List[bool] = None,
        uv_lock: bool = False,
    ):
        """
        Draws the BoxModel direct into the world
        WARNING: use batches for better performance
        :param instance: the instance to ues for rendering
        :param position: the position to draw on
        :param rotation: the rotation to draw with
        :param uv_lock: if the uv's should be locked in place or not
        :param active_faces: which faces to draw
        """
        collected_data = self.get_prepared_box_data(
            instance, position, rotation, active_faces=active_faces, uv_lock=uv_lock
        )
        self.draw_prepared_data(collected_data)

    def add_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        batch,
        rotation: typing.Tuple[float, float, float],
        face: EnumSide,
        uv_lock=False,
    ):
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)
        face = face.rotate(rotation)

        return self.add_to_batch(
            instance,
            position,
            batch,
            rotation,
            active_faces=face,
            uv_lock=uv_lock,
        )

    def draw_face(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
        face: EnumSide,
        uv_lock=False,
    ):
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)
        face = face.rotate(rotation)

        return self.draw(
            instance,
            position,
            rotation,
            active_faces=face,
            uv_lock=uv_lock,
        )

    def copy(self, new_model=None):
        # todo: do we really need to re-parse the model data?
        return BoxModel().parse_mc_data(
            self.data, new_model if new_model is not None else self.model
        )


@onlyInClient()
class RawBoxModel(AbstractBoxModel):
    """
    A non-model-bound BoxModel class
    """

    def copy(self) -> "AbstractBoxModel":
        return type(self)(
            self.relative_position,
            self.size,
            self.texture,
            self.texture_region,
            self.rotation,
            self.rotation_center,
        )

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
                mcpython.engine.ResourceLoader.read_pyglet_image(texture).get_texture()
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

        self.vertex_provider: typing.Optional[VertexProvider] = None

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
        self.vertex_provider = VertexProvider.create(
            tuple(self.relative_position),
            tuple(self.size),
            tuple(self.rotation_center),
            tuple(self.__rotation),
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
        return sum(
            itertools.chain(
                *self.vertex_provider.get_vertex_data(
                    position, rotation, rotation_center
                )
            ),
            tuple(),
        )

    def add_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        return batch.add(
            4 * 6,
            pyglet.gl.GL_QUADS,
            self.texture,
            ("v3d/static", vertices),
            ("t2f/static", self.texture_cache),
        )

    def add_face_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        face: typing.Optional[typing.Union[typing.Iterable[int], EnumSide]],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        result = []
        for i in range(6):
            if i in face if isinstance(face, int) else face.index == i:
                continue

            t = self.texture_cache[i * 8 : i * 8 + 8]
            v = vertices[i * 12 : i * 12 + 12]
            result.append(
                batch.add(
                    4,
                    pyglet.gl.GL_QUADS,
                    self.texture,
                    ("v3d/static", v),
                    ("t2f/static", t),
                )
            )
        return result

    def draw(
        self,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)

        if self.texture is not None:
            self.texture.set_state()

        pyglet.graphics.draw(
            4 * 6,
            pyglet.gl.GL_QUADS,
            ("v3d/static", vertices),
            ("t2f/static", self.texture_cache),
        )

        if self.texture is not None:
            self.texture.unset_state()


@onlyInClient()
class MutableRawBoxModel(RawBoxModel):
    def add_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        return batch.add(
            4 * 6,
            pyglet.gl.GL_QUADS,
            self.texture,
            ("v3f/dynamic", vertices),
            ("t2f/dynamic", self.texture_cache),
        )

    def mutate_add_to_batch(
        self,
        previous: pyglet.graphics.vertexdomain.VertexList,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        previous.vertices[:] = vertices

    def add_face_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        face: typing.Optional[typing.Union[typing.Iterable[int], EnumSide]],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        result = []
        for i in range(6):
            if (
                i not in face
                if isinstance(face, int)
                else (face is not None and face.index == i)
            ):
                continue

            t = self.texture_cache[i * 8 : i * 8 + 8]
            v = vertices[i * 12 : i * 12 + 12]
            result.append(
                batch.add(
                    4,
                    pyglet.gl.GL_QUADS,
                    self.texture,
                    ("v3f/dynamic", v),
                    ("t2f/dynamic", t),
                )
            )
        return result

    def mutate_add_face_to_batch(
        self,
        previous: typing.List[pyglet.graphics.vertexdomain.VertexList],
        position: typing.Tuple[float, float, float],
        face: typing.Optional[typing.Union[typing.Iterable[int], EnumSide]],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        for i in range(6):
            if (
                i not in face
                if isinstance(face, int)
                else (face is not None and face.index == i)
            ):
                continue

            v = vertices[i * 12 : i * 12 + 12]
            previous.pop(0).vertices[:] = v


@onlyInClient()
class ColoredRawBoxModel(RawBoxModel):
    def add_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
        color=(1, 1, 1, 1),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        return batch.add(
            24,
            pyglet.gl.GL_QUADS,
            self.texture,
            ("v3d/static", vertices),
            ("t2f/static", self.texture_cache),
            ("c4f", color * 24),
        )

    def add_face_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        face: typing.Union[typing.Iterable[int], EnumSide],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
        color=(1, 1, 1, 1),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)
        result = []
        for i in range(6):
            if (
                i not in face
                if isinstance(face, int)
                else (face is not None and face.index == i)
            ):
                continue

            t = self.texture_cache[i * 8 : i * 8 + 8]
            v = vertices[i * 12 : i * 12 + 12]
            result.append(
                batch.add(
                    4,
                    pyglet.gl.GL_QUADS,
                    self.texture,
                    ("v3d/static", v),
                    ("t2f/static", t),
                    ("c4f", color * 4),
                )
            )
        return result

    def draw(
        self,
        position: typing.Tuple[float, float, float],
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
        color=(1, 1, 1, 1),
    ):
        vertices = self.get_vertices(position, rotation, rotation_center)

        if self.texture is not None:
            self.texture.set_state()

        pyglet.graphics.draw(
            24,
            pyglet.gl.GL_QUADS,
            ("v3d/static", vertices),
            ("t2f/static", self.texture_cache),
            ("c4f", color * 24),
        )

        if self.texture is not None:
            self.texture.unset_state()
