"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import pyglet

from mcpython import shared
from mcpython import logger
import mcpython.client.texture.TextureAtlas as TextureAtlas
import mcpython.client.rendering.model.BoxModel
import mcpython.util.enums


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

        self.boxmodels = (
            []
            if not self.parent
            else [x.copy(new_model=self) for x in self.parent.boxmodels]
        )

        if "elements" in data:
            self.boxmodels.clear()
            for element in data["elements"]:
                self.boxmodels.append(
                    mcpython.client.rendering.model.BoxModel.BoxModel(element, self)
                )

    def add_face_to_batch(
        self,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        if not self.drawable:
            raise NotImplementedError(
                "can't draw an model '{}' which has not defined textures".format(
                    self.name
                )
            )
        data = []
        for boxmodel in self.boxmodels:
            data += boxmodel.add_face_to_batch(
                position, batch, config["rotation"], face
            )
        return data

    def draw_face(
        self,
        position: typing.Tuple[float, float, float],
        config: dict,
        face: mcpython.util.enums.EnumSide,
    ):
        if not self.drawable:
            raise NotImplementedError(
                "can't draw an model '{}' which has not defined textures".format(
                    self.name
                )
            )
        for boxmodel in self.boxmodels:
            boxmodel.draw_face(
                position,
                config["rotation"],
                face,
                uv_lock=config.setdefault("uvlock", False),
            )

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