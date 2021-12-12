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
import asyncio
import typing

import deprecation
import mcpython.client.rendering.model.BoxModel
import mcpython.client.texture.TextureAtlas as TextureAtlas
import mcpython.engine.ResourceLoader
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.client.rendering.model.api import IBlockStateRenderingTarget
from mcpython.client.texture.AnimationManager import animation_manager
from mcpython.engine import logger
from mcpython.util.enums import EnumSide
from pyglet.graphics.vertexdomain import VertexList


class Model:
    """
    Class representing a (block) model from the file system
    Contains the needed API functions to render the model
    """

    def __init__(self, name: str, modname: str):
        self.name = name
        self.modname = modname
        self.parent = None
        self.used_textures = {}
        self.animated_textures = {}
        self.texture_addresses = {}
        self.texture_names = {}
        self.drawable = True
        self.texture_atlas = None
        self.box_models = []

    async def parse_from_data(self, data: dict):
        self.parent = data["parent"] if "parent" in data else None

        # do some parent copying stuff
        if self.parent is not None:
            await self.parse_parent_data()

        # check out assigned textures
        if "textures" in data:
            for name in data["textures"].keys():
                self.parse_texture(data["textures"][name], name)

        self.bake_textures()

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

        return self

    def bake_textures(self):
        """
        Informs the texture bake system about our new textures we want to be in there
        Prepares the texture_addresses attribute with the location of the texture
        """
        to_add = []
        for name in self.used_textures:
            to_add.append((name, self.used_textures[name]))

        add = TextureAtlas.handler.add_image_files([x[1] for x in to_add], self.modname)
        for i, (name, _) in enumerate(to_add):
            if name not in self.animated_textures:
                self.texture_addresses[name] = add[i][0]

            self.texture_atlas = add[i][1]

    async def parse_parent_data(self):
        if ":" not in self.parent:
            self.parent = "minecraft:" + self.parent

            if "minecraft" not in self.name and ":" in self.name:
                logger.println(
                    "[WARN] unsafe access to model '{}' from '{}'; use namespaced access here! (deprecated)".format(
                        self.parent, self.name
                    )
                )

        if self.parent not in shared.model_handler.models:
            await shared.model_handler.load_model(self.parent)

        if self.parent not in shared.model_handler.models:
            self.parent = None
            logger.println(
                f"[FATAL] causing model {self.name} to not bake its parent references"
            )
            return

        self.parent = shared.model_handler.models[self.parent]

        if self.parent is not None:
            self.used_textures = self.parent.used_textures.copy()
            self.texture_names = self.parent.texture_names.copy()

    def parse_texture(self, texture: str, name: str):
        if not isinstance(texture, str):
            logger.println("invalid texture", texture, name, self.name)
            self.texture_names[name] = "assets/missing_texture.png"
            return

        if not texture.startswith("#"):
            if ":" in texture:
                texture_f = "assets/{}/textures/{}.png".format(*texture.split(":"))
            elif not texture.endswith(".png"):
                texture_f = "assets/minecraft/textures/{}.png".format(texture)
            else:
                texture_f = texture

            # todo: add a way to disable animated textures
            if mcpython.engine.ResourceLoader.exists(texture_f + ".mcmeta"):
                self.animated_textures[
                    name
                ] = animation_manager.prepare_animated_texture(texture)

            self.used_textures[name] = texture

        else:  # so, the target texture itself is a variable, so we cannot load them here
            self.drawable = False
            self.texture_names[name] = texture

    def prepare_rendering_data_multi_face(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        config: dict,
        faces: int,
        previous: typing.Tuple[typing.List[float], typing.List[float]] = None,
        batch: pyglet.graphics.Batch = None,
        scale: float = 1,
    ) -> typing.Tuple[
        typing.Tuple[
            typing.List[float], typing.List[float], typing.List[float], typing.List
        ],
        typing.Any,
    ]:
        """
        Collects the vertex and texture data for a block at the given position with given configuration
        :param instance: the instance to draw
        :param position: the offset position
        :param config: the configuration
        :param faces: the faces
        :param previous: previous collected data, as a tuple of vertices, texture coords
        :param batch: the batch to use
        :param scale: the scale to use
        :return: a tuple of vertices and texture coords, and an underlying BoxModel for some identification stuff
        """

        collected_data = ([], [], [], []) if previous is None else previous

        # If this is true, we cannot render this model as stuff is not fully linked
        if not self.drawable:
            logger.println(
                f"[BLOCK MODEL][FATAL] can't draw the model '{self.name}' "
                f"(which has not defined textures) at {position}"
            )
            return collected_data, None

        if not self.box_models:
            return collected_data, None

        # todo: can we parse this beforehand and store as an attribute?
        rotation = config["rotation"]
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)

        for box_model in self.box_models:
            box_model.prepare_rendering_data_multi_face(
                instance,
                position,
                rotation,
                faces,
                previous=collected_data,
                batch=batch,
                scale=scale,
            )

        return collected_data, self.box_models[0]

    def add_faces_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        config: dict,
        faces: int,
        scale: float = 1,
    ) -> typing.Iterable[VertexList]:
        """
        Adds given faces to the given batch system
        Parameters same as prepare_rendering_data_multi_face
        """
        if not isinstance(faces, int):
            raise ValueError(faces)

        collected_data, box_model = self.prepare_rendering_data_multi_face(
            instance,
            position,
            config,
            faces,
            batch=batch,
            scale=scale,
        )
        if box_model is None:
            return tuple()

        return tuple(collected_data[3]) + tuple(
            box_model.add_prepared_data_to_batch(collected_data, batch)
        )

    def draw_face(
        self,
        instance,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide | int,
        scale: float = 1,
    ):
        """
        Similar to add_face_to_batch, but does it in-place without a batches
        Use batches wherever possible!
        """
        if isinstance(face, EnumSide):
            face = face.bitflag
        collected_data, box_model = self.prepare_rendering_data_multi_face(
            instance,
            position,
            config,
            face,
            scale=scale,
        )
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

        if name in self.animated_textures:
            return self.animated_textures[name]

        if name in self.texture_names:
            return self.get_texture_position(self.texture_names[name])

        if name.startswith("#"):
            n = name[1:]
            if n in self.texture_addresses:
                return self.texture_addresses[n]

            if n in self.animated_textures:
                return self.animated_textures[n]

            if n in self.texture_names:
                return self.get_texture_position(self.texture_names[n])

        return 0, 0

    @deprecation.deprecated()
    def get_prepared_data_for_scaled(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
        scale: float,
        previous: typing.Tuple[typing.List[float], typing.List[float]] = None,
        batch=None,
    ) -> typing.Tuple[
        typing.Tuple[
            typing.List[float], typing.List[float], typing.List[float], typing.List
        ],
        typing.Any,
    ]:
        return self.prepare_rendering_data_multi_face(
            instance,
            position,
            config,
            face.bitflag,
            scale=scale,
            previous=previous,
            batch=batch,
        )

    @deprecation.deprecated()
    def add_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        collected_data, box_model = self.get_prepared_data_for(
            instance, position, config, face
        )
        if box_model is None:
            return tuple()

        return box_model.add_prepared_data_to_batch(collected_data, batch)

    @deprecation.deprecated()
    def get_prepared_data_for(
        self,
        instance: IBlockStateRenderingTarget,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
        previous: typing.Tuple[typing.List[float], typing.List[float]] = None,
        batch=None,
    ) -> typing.Tuple[
        typing.Tuple[
            typing.List[float], typing.List[float], typing.List[float], typing.List
        ],
        typing.Any,
    ]:
        return self.prepare_rendering_data_multi_face(
            instance, position, config, face.bitflag, previous=previous, batch=batch
        )

    @deprecation.deprecated()
    def draw_face_scaled(
        self,
        instance,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
        scale: float,
    ):
        self.draw_face(instance, position, config, face, scale=scale)
