"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.client.rendering.model.Model
import deprecation


@deprecation.deprecated("dev2-2", "a1.5.0")
class ModelFactory:
    @deprecation.deprecated("dev2-2", "a1.5.0")
    def __init__(self, name: str, parent="minecraft:block/block"):
        self.name = name
        self.parent = parent
        self.elements = []
        self.textures = {}

    def add_drawing_box(self, position, size, texturenames):
        for i, element in enumerate(texturenames):
            if not element.startswith("#"):
                texturenames[i] = "#" + element
        self.elements.append(
            {
                "from": position,
                "to": [position[i] + size[i] for i in range(3)],
                "faces": {
                    "down": {"texture": texturenames[1], "cullface": "down"},
                    "up": {"texture": texturenames[0], "cullface": "up"},
                    "north": {"texture": texturenames[2], "cullface": "north"},
                    "south": {"texture": texturenames[4], "cullface": "south"},
                    "west": {"texture": texturenames[5], "cullface": "west"},
                    "east": {"texture": texturenames[3], "cullface": "east"},
                },
            }
        )
        return self

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def set_texture(self, name, texturefile):
        self.textures[name] = texturefile
        return self

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def finish(self):
        data = {"parent": self.parent}
        if len(self.elements) > 0:
            data["elements"] = self.elements
        if len(self.textures) > 0:
            data["textures"] = self.textures
        G.modelhandler.models[self.name] = mcpython.client.rendering.model.Model.Model(
            data, self.name, self.name.split(":")[0]
        )