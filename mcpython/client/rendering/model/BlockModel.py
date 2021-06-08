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
from mcpython import logger, shared


class Model:
    """
    Class representing an model from the file system
    """

    def __init__(self, data: dict, name: str, modname: str):
        self.data = data
        self.name = name
        self.parent = data["parent"] if "parent" in data else None
        self.used_textures = {}
        self.texture_addresses = {}
        self.texture_names = {}
        self.drawable = True

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

        if "textures" in data:
            for name in data["textures"].keys():
                texture = data["textures"][name]
                if not texture.startswith("#"):
                    self.used_textures[name] = texture
                else:
                    self.drawable = False
                    self.texture_names[name] = texture

        to_add = []
        for name in self.used_textures:
            to_add.append((name, self.used_textures[name]))
        add = TextureAtlas.handler.add_image_files([x[1] for x in to_add], modname)
        self.texture_atlas = None

        for i, (name, _) in enumerate(to_add):
            self.texture_addresses[name] = add[i][0]
            self.texture_atlas = add[i][1]

        self.box_models = (
            []
            if not self.parent
            else [x.copy(new_model=self) for x in self.parent.box_models]
        )

        if "elements" in data:
            self.box_models.clear()
            for element in data["elements"]:
                self.box_models.append(
                    mcpython.client.rendering.model.BoxModel.BoxModel(element, self)
                )

    def get_prepared_data_for(self, position, config, face):
        if not self.drawable:
            logger.println(
                f"[BLOCK MODEL][FATAL] can't draw an model '{self.name}' which has not defined textures"
            )
            return [], None

        rotation = config["rotation"]
        if rotation == (90, 90, 0):
            rotation = (0, 0, 90)

        collected_data = [], []
        box_model = None
        for box_model in self.box_models:
            a, b = box_model.get_prepared_box_data(
                position,
                rotation,
                face.rotate((0, -90, 0))
                if rotation[1] % 180 != 90
                else face.rotate((0, 90, 0)),
            )
            collected_data[0].extend(a)
            collected_data[1].extend(b)
        return collected_data, box_model

    def add_face_to_batch(
        self,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        collected_data, box_model = self.get_prepared_data_for(position, config, face)
        if box_model is None:
            return tuple()
        return box_model.add_prepared_data_to_batch(collected_data, batch)

    def draw_face(
        self,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        collected_data, box_model = self.get_prepared_data_for(position, config, face)
        if box_model is None:
            return
        box_model.draw_prepared_data(collected_data)

    def get_texture_position(
        self, name: str
    ) -> typing.Optional[typing.Tuple[int, int]]:
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
