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

import mcpython.client.rendering.model.BoxModel
import mcpython.engine.ResourceLoader
import pyglet
from mcpython.util.annotation import onlyInClient

RENDERERS = []
TEXTURES = {}


@onlyInClient()
class EntityRenderer:
    def __init__(self, name):
        self.name = name
        self.path = "assets/{}/config/entity/{}.json".format(*name.split(":"))
        self.data = None
        self.box_models = {}
        self.states = {}
        self.texture_size = None
        asyncio.get_event_loop().run_until_complete(self.reload())
        RENDERERS.append(self)

    async def reload(self):
        """
        reloads from file
        concept: every entity has an state which can be rendered (similar to blockstates). Every state contains multiple
            boxes, which can be shared across multiple states. You can select from every level the rendering position
            and rotation, but only on the lowest level (the level of the boxes) you can select the parameters of the box
            itself
        file format:
        {
            "boxes": {
                <name>: {
                    "texture": <texturepath>,
                    "texture_size": <how big the texture is normally>,
                    "position": <relative position to center>,
                    "rotation": <relative rotation to center>,
                    "size": <size of the box>,
                    "center": <center of rotation>
                }
            },
            "states": {
                <name>: {
                    "boxes": [
                        {
                            "box": <box name>,
                            "rotation": <rotation relative to center>,
                            "center": <center of rotation>,
                            "position": <position relative to center>
                        }
                    ]
                }
            }
        }
        """
        self.data = mcpython.engine.ResourceLoader.read_json(self.path)
        self.box_models.clear()
        self.states.clear()
        reloaded = []
        for box_name in self.data["boxes"]:
            box = self.data["boxes"][box_name]
            texture = box["texture"]
            self.texture_size = box["texture_size"]
            if texture in TEXTURES and texture in reloaded:
                group = TEXTURES[texture]
            else:
                if mcpython.engine.ResourceLoader.exists(texture):
                    group = TEXTURES[texture] = pyglet.graphics.TextureGroup(
                        mcpython.engine.ResourceLoader.read_pyglet_image(
                            texture
                        ).get_texture()
                    )
                else:
                    group = TEXTURES[texture] = pyglet.graphics.TextureGroup(
                        mcpython.engine.ResourceLoader.read_pyglet_image(
                            "assets/missing_texture.png"
                        ).get_texture()
                    )
                reloaded.append(texture)
            if "invert_indexes" not in box or not box["invert_indexes"]:
                uv = [
                    tuple(
                        [
                            float(x) / self.texture_size[i % 2]
                            for i, x in enumerate(e.split("|"))
                        ]
                    )
                    for e in box["uv"]
                ]
            else:
                uv = [
                    tuple(
                        [
                            (
                                float(x)
                                if i % 2 == 0
                                else self.texture_size[i % 2] - float(x)
                            )
                            / self.texture_size[i % 2]
                            for i, x in enumerate(e.split("|"))
                        ]
                    )
                    for e in box["uv"]
                ]
            self.box_models[
                box_name
            ] = mcpython.client.rendering.model.BoxModel.RawBoxModel(
                box["position"] if "position" in box else (0, 0, 0),
                tuple([e / 16 for e in box["size"]]),
                group,
                uv,
                box["rotation"] if "rotation" in box else (0, 0, 0),
                box["center"] if "center" in box else (0, 0, 0),
            )
        for state in self.data["states"]:
            d = self.data["states"][state]
            self.states[state] = d["boxes"]

    def draw(self, entity_or_position, state, rotation=(0, 0, 0), part_rotation=None):
        """
        Draws the EntityRenderer at the given position
        :param entity_or_position: the entity to render or the position to render at
        :param state: the state to render, as in the model of the entity
        :param rotation: the rotation to use; as (rx, ry, rz)
        :param part_rotation: the rotation of every part, as a dict of model part -> (rx, ry, rz), calculated onto
            the "other" rotations
        """
        x, y, z = (
            entity_or_position.position
            if not isinstance(entity_or_position, tuple)
            else entity_or_position
        )
        for ibox, d in enumerate(self.states[state]):
            box = self.box_models[d["box"]]
            rotation_2 = (0, 0, 0) if "rotation" not in d else d["rotation"]
            rotation_center = (0, 0, 0) if "center" not in d else d["center"]
            dx, dy, dz = (0, 0, 0) if "position" not in d else d["position"]
            box.draw(
                (x + dx, y + dy, z + dz),
                rotation=tuple(
                    [
                        rotation[i]
                        + rotation_2[i]
                        + (
                            0
                            if part_rotation is None or d["box"] not in part_rotation
                            else part_rotation[d["box"]][i]
                        )
                        for i in range(3)
                    ]
                ),
                rotation_center=rotation_center,
            )

    def draw_box(
        self,
        entity_or_position,
        box_name: str,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        rotation_center=(0, 0, 0),
    ):
        """
        Renders a single box of the model
        :param entity_or_position: the position to render at or the entity to render
        :param box_name: the box name
        :param position: the offset
        :param rotation: the rotation
        :param rotation_center: the center to rotate around
        """
        x, y, z = (
            entity_or_position.position
            if not isinstance(entity_or_position, tuple)
            else entity_or_position
        )
        box = self.box_models[box_name]
        box.draw(
            (x + position[0], y + position[1], z + position[2]),
            rotation=rotation,
            rotation_center=rotation_center,
        )

    def add_to_batch(
        self,
        batch: pyglet.graphics.Batch,
        entity_or_position,
        state,
        rotation=(0, 0, 0),
        part_rotation=None,
    ):
        """
        Adds the entity to a batch. Useful mostly for static entities like static complex block elements

        WARNING: this is not-mutable
        WARNING: batch  M U S T  be rendered in an 3d environment with, if the texture needs it, alpha enabled

        :param batch: the batch to use
        :param entity_or_position: the entity to add
        :param state: the state to add
        :param rotation: the rotation to use
        :param part_rotation: the rotation of every part
        :return: an list of vertex-objects created with the batch
        """
        data = []
        x, y, z = (
            entity_or_position.position
            if not isinstance(entity_or_position, tuple)
            else entity_or_position
        )
        for d in self.states[state]:
            box = self.box_models[d["box"]]
            rotation_2 = (0, 0, 0) if "rotation" not in d else d["rotation"]
            rotation_center = (0, 0, 0) if "center" not in d else d["center"]
            dx, dy, dz = (0, 0, 0) if "position" not in d else d["position"]
            data.extend(
                box.add_to_batch(
                    batch,
                    (x + dx, y + dy, z + dz),
                    rotation=tuple(
                        [
                            rotation[i]
                            + rotation_2[i]
                            + (
                                0
                                if part_rotation is None
                                or d["box"] not in part_rotation
                                else part_rotation[d["box"]][i]
                            )
                            for i in range(3)
                        ]
                    ),
                    rotation_center=rotation_center,
                )
            )
        return data
