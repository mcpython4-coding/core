"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.datagen.Configuration


class EntityModelGenerator(mcpython.datagen.Configuration.IDataGenerator):
    def __init__(self, config, name):
        super().__init__(config)
        self.name = name
        self.boxes = {}
        self.states = {}

    def add_box(self, name: str, texture: str, tex_size: tuple, position: tuple, rotation: tuple, size: tuple,
                center: tuple, uv=None):
        if uv is None:
            uv = [(0, 0, 1, 1)] * 6
        self.boxes[name] = texture, tex_size, position, rotation, size, center, uv

    def add_state(self, name: str, *boxes):
        self.states[name] = boxes

    def generate(self):
        data = {"boxes": {}, "states": {}}

        for key in self.boxes:
            texture, tex_size, position, rotation, size, center, uv = self.boxes[key]
            data["boxes"][key] = {"texture": texture, "texture_size": tex_size, "position": position,
                                  "rotation": rotation, "size": size, "center": center, "uv": uv}

        for key in self.states:
            d = []
            for box in self.states[key]:
                if type(box) == tuple:
                    e = {"box": box[0]}
                    if len(box) > 1: e["position"] = box[1]
                    if len(box) > 2: e["rotation"] = box[2]
                    if len(box) > 3: e["center"] = box[3]
                else:
                    e = {"box": box}
                d.append(e)

        self.config.write_json(data, "assets", "config/entity", self.name+".json")
