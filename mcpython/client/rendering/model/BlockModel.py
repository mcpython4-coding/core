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

import mcpython.client.rendering.model.BoxModel
import mcpython.client.texture.TextureAtlas as TextureAtlas
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.api import IBlockStateRenderingTarget
from mcpython.engine import logger
from pyglet.graphics.vertexdomain import VertexList


class Model:
    """
    Class representing a (block) model from the file system
    """

    def __init__(self, data: dict, name: str, modname: str):
        self.data = data
        self.name = name
        self.parent = data["parent"] if "parent" in data else None
        self.used_textures = {}
        self.texture_addresses = {}
        self.texture_names = {}
        self.drawable = True

        # do some parent copying stuff
        if self.parent is not None:
            if ":" not in self.parent:
                self.parent = "minecraft:" + self.parent
                if "minecraft" not in name and ":" in name:
                    logger.println(
                        "[WARN] unsafe access to model '{}' from '{}'".format(
                            self.parent, name
                        )
                    )
            if self.parent not in shared.model_handler.models:
                shared.model_handler.load_model(self.parent)
            self.parent = shared.model_handler.models[self.parent]
            self.used_textures = self.parent.used_textures.copy()
            self.texture_names = self.parent.texture_names.copy()

        # check out assigned textures
        if "textures" in data:
            for name in data["textures"].keys():
                texture = data["textures"][name]
                if not texture.startswith("#"):
                    self.used_textures[name] = texture
                else:
                    self.drawable = False
                    self.texture_names[name] = texture

        # inform the texture bake system about our new textures we want to be in there
        to_add = []
        for name in self.used_textures:
            to_add.append((name, self.used_textures[name]))
        add = TextureAtlas.handler.add_image_files([x[1] for x in to_add], modname)
        self.texture_atlas = None

        for i, (name, _) in enumerate(to_add):
            self.texture_addresses[name] = add[i][0]
            self.texture_atlas = add[i][1]

        # prepare the box models from parent
        self.box_models = (
            []
            if not self.parent or "elements" in data
            else [x.copy(new_model=self) for x in self.parent.box_models]
        )

        # load local elements
        if "elements" in data:
            for element in data["elements"]:
                self.box_models.append(
                    mcpython.client.rendering.model.BoxModel.BoxModel().parse_mc_data(
                        element, self
                    )
                )

    def get_prepared_data_for(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
        previous: typing.Tuple[typing.List[float], typing.List[float]] = None,
    ) -> typing.Tuple[typing.Tuple[typing.List[float], typing.List[float], typing.List[float]], typing.Any]:
        """
        Collects the vertex and texture data for a block at the given position with given configuration
        :param instance: the instance to draw
        :param position: the offset position
        :param config: the configuration
        :param face: the face
        :param previous: previous collected data, as a tuple of vertices, texture coords
        :return: a tuple of vertices and texture coords, and an underlying BoxModel for some identification stuff
        """

        # If this is true, we cannot render this model as stuff is not fully linked
        if not self.drawable:
            logger.println(
                f"[BLOCK MODEL][FATAL] can't draw an model '{self.name}' which has not defined textures at {position}"
            )
            return ([], [], []), None

        rotation = config["rotation"]
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)

        collected_data = ([], [], []) if previous is None else previous
        box_model = None

        for box_model in self.box_models:
            box_model.get_prepared_box_data(
                instance,
                position,
                rotation,
                face.rotate((0, -90, 0))
                if rotation[1] % 180 != 90
                else face.rotate((0, 90, 0)),
                previous=collected_data,
            )

        return collected_data, box_model

    def add_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ) -> typing.Iterable[VertexList]:
        """
        Adds a given face to the batch
        Simply wraps a get_prepared_data_for call around the box_model.add_prepared_data_to_batch-call
        """
        collected_data, box_model = self.get_prepared_data_for(instance, position, config, face)
        if box_model is None:
            return tuple()

        return box_model.add_prepared_data_to_batch(collected_data, batch)

    def draw_face(
        self,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        """
        Similar to add_face_to_batch, but does it in-place without a batches
        Use batches wherever possible!
        """
        collected_data, box_model = self.get_prepared_data_for(position, config, face)
        if box_model is None:
            return

        box_model.draw_prepared_data(collected_data)

    def get_texture_position(
        self, name: str
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Helper method resolving a texture name to texture coords
        :param name: the name of the texture
        :return: a tuple of x, y of the texture location, defaults to 0, 0 in case of an error
        """
        if not self.drawable:
            return 0, 0

        if name in self.texture_addresses:
            return self.texture_addresses[name]

        if name in self.texture_names:
            return self.get_texture_position(self.texture_names[name])

        if name.startswith("#"):
            n = name[1:]
            if n in self.texture_addresses:
                return self.texture_addresses[n]

            if n in self.texture_names:
                return self.get_texture_position(self.texture_names[n])

        return 0, 0
