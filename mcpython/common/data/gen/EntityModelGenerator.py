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
from mcpython.common.data.gen.DataGeneratorManager import (
    IDataGenerator,
    DataGeneratorInstance,
)


class EntityModelGenerator(IDataGenerator):
    """
    Data generator for creating an entity model file
    """

    def __init__(self, name):
        self.name = name
        self.boxes = {}
        self.states = {}
        self.y_inverted = False

    def setInvertedY(self, state=True):
        """
        will set all y indexes to their other values
        :param state: the state to set to, default is True
        """
        self.y_inverted = state
        return self

    def add_box(
        self,
        name: str,
        texture: str,
        tex_size: tuple,
        position: tuple,
        rotation: tuple,
        size: tuple,
        center: tuple,
        uv=None,
    ):
        """
        will add one new box to the entity model
        :param name: the name of the box
        :param texture: the texture of the box as an ResourceLocation-string
        :param tex_size: the size of the texture, needed for all subsequent calculations
        :param position: the position of the box relative to the entity origin
        :param rotation: the rotation of the box in degrees
        :param size: the size of the box, in 16 units = 1 block length
        :param center: the center of the rotation
        :param uv: the uv's to use
        """
        if uv is None:
            uv = [(0, 0, 1, 1)] * 6
        if (
            type(uv) == tuple and len(uv) == 2
        ):  # Ok, we have the offset in x and y direction, so parse it in the normal way
            dx, dy = uv
            sx, sy, sz = size
            uv = [
                (dx + sz + sx, dy + sz, dx + sz + 2 * sx, dy),
                (dx + sz, dy, dx + sz + sx, dy + sz),
                (dx + sz, dy + sz, dx + sz + dx, dy + sz + sy),
                (dx + 2 * sz + sx, dy + sz, dx + 2 * sz + 2 * dx, dy + sz + sy),
                (dx, dy + sz, dy + sz, dy + sz + sy),
                (dx + sz + sx, dy + sz, dx + 2 * sz + sx, dy + sz + sy),
            ]
        self.boxes[name] = texture, tex_size, position, rotation, size, center, uv
        return self

    def add_state(self, name: str, *boxes):
        """
        adds an state for rendering the entity
        :param name: the name of the state
        :param boxes: the boxes to include
        """
        self.states[name] = boxes
        return self

    def dump(self, generator: DataGeneratorInstance):
        data = {"boxes": {}, "states": {}}

        for key in self.boxes:
            texture, tex_size, position, rotation, size, center, uv = self.boxes[key]

            # create uv strings from tuples
            for i, entry in enumerate(uv):
                if type(entry) == tuple:
                    uv[i] = "|".join(
                        [
                            str(
                                e
                                if not self.y_inverted and i % 2 != 0
                                else size[1] - float(e)
                            )
                            for i, e in enumerate(entry)
                        ]
                    )

            data["boxes"][key] = {
                "texture": texture,
                "texture_size": tex_size,
                "position": [e / 16 for e in position],
                "rotation": rotation,
                "size": size,
                "center": [e / 16 for e in center],
                "uv": uv,
            }

        for key in self.states:
            boxes = []
            for box in self.states[key]:
                if type(box) == tuple:
                    e = {"box": box[0]}
                    if len(box) > 1:
                        e["position"] = box[1]
                    if len(box) > 2:
                        e["rotation"] = box[2]
                    if len(box) > 3:
                        e["center"] = box[3]
                else:
                    e = {"box": box}
                boxes.append(e)
            data["states"][key] = {"boxes": boxes}

        return data

    def get_default_location(self, generator: DataGeneratorInstance, name: str):
        return (
            "assets/{}/models/entity/{}.json".format(*name.split(":"))
            if ":" in name
            else "assets/{}/models/entity/{}.json".format(
                generator.default_namespace, name
            )
        )
