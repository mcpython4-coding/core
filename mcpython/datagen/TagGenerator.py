"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.datagen.Configuration


class TagGenerator(mcpython.datagen.Configuration.IDataGenerator):
    def __init__(self, config, group: str, name: str, override=False):
        super().__init__(config)
        self.group = group
        self.name = name
        self.override = override
        self.affected = set()

    def add_affected(self, *affected):
        self.affected += affected

    def generate(self):
        self.config.write_json({"replace": self.override, "values": list(self.affected)}, "data", "tags/"+self.group,
                               self.name+".json")

