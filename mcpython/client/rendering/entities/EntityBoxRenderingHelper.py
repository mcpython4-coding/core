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

import mcpython.client.texture.TextureAtlas
import mcpython.engine.ResourceLoader
import pyglet
from mcpython import shared
from mcpython.util import opengl as opengl_util
from mcpython.util import texture as texture_util


class EntityBoxInstance:
    """
    The box rendered for entities [in the future]
    """

    class MutableEntityBox:
        """
        Mutator for the underlying VertexList
        Handles the vertex calculation
        """

        def __init__(
            self,
            source: "EntityBoxInstance",
            buffer: pyglet.graphics.vertexdomain.VertexList,
            position,
            rotation,
        ):
            self.source = source
            self.buffer = buffer
            self.position = position
            self.rotation = rotation

        def update(self):
            vertices, uvs = self.source.get_draw_info(self.position, self.rotation)
            self.buffer.vertices = vertices
            self.buffer.tex_coords = uvs
            return self

        def get_underlying(self) -> pyglet.graphics.vertexdomain.VertexList:
            return self.buffer

        def delete(self):
            self.buffer.delete()
            return self

    def __init__(
        self,
        texture_path: str,
        sheet_size: typing.Tuple[int, int],
        texture_size: typing.Tuple[int, int, int],
        box_size: typing.Tuple[float, float, float],
    ):
        self.texture_path = texture_path
        self.sheet_size = sheet_size
        self.texture_size = texture_size
        self.box_size = box_size

        self.texture_group: pyglet.graphics.TextureGroup = None

        self.tex_coords_cache: typing.Optional[typing.List[float]] = []
        self.rotation2vertices: typing.Dict[
            typing.Tuple[float, float, float], typing.List[int]
        ] = {}

    def draw(
        self,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
    ):
        vertices, uvs = self.get_draw_info(position, rotation)
        self.texture_group.set_state()
        pyglet.graphics.draw(6, pyglet.gl.GL_QUADS, ("v3d", vertices), ("t2d", uvs))
        self.texture_group.unset_state()

    def add_to_batch_static(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
    ) -> pyglet.graphics.vertexdomain.VertexList:
        vertices, uvs = self.get_draw_info(position, rotation)
        return batch.add(
            6, pyglet.gl.GL_QUADS, self.texture_group, ("v3d", vertices), ("t2d", uvs)
        )

    def add_to_batch_mutable(
        self,
        batch: pyglet.graphics.Batch,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
    ) -> MutableEntityBox:
        vertices, uvs = self.get_draw_info(position, rotation)
        buffer = batch.add(
            6, pyglet.gl.GL_QUADS, self.texture_group, ("v3d", vertices), ("t2d", uvs)
        )
        return EntityBoxInstance.MutableEntityBox(self, buffer, position, rotation)

    def get_draw_info(
        self,
        position: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
    ) -> typing.Tuple[typing.List[float], typing.List[float]]:
        return (
            self.calculate_vertices_variant(position, rotation),
            self.tex_coords_cache
            if self.tex_coords_cache is not None
            else self.calculate_texture_coords(),
        )

    def invalidate(self):
        """
        Forces a recalculation of the whole cache based on initial parameters
        """
        self.rotation2vertices.clear()
        self.tex_coords_cache.clear()

    def calculate_texture_coords(self) -> typing.List[float]:
        pass

    def calculate_default_vertices(self) -> typing.List[float]:
        pass

    def get_rotated_vertices_variant(
        self, rotation: typing.Tuple[float, float, float]
    ) -> typing.List[float]:
        pass

    def calculate_vertices_variant(
        self,
        offset: typing.Tuple[float, float, float],
        rotation: typing.Tuple[float, float, float],
    ) -> typing.List[float]:
        pass
