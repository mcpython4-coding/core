"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.data.datagen.Configuration


class LanguageGenerator(mcpython.datagen.Configuration.IDataGenerator):
    def __init__(self, config: mcpython.datagen.Configuration.DataGeneratorConfig, lang_name: str):
        super().__init__(config)
        self.lang_name = lang_name
        self.table = {}

    def add_key(self, key: str, value: str):
        self.table[key] = value
        return self

    def generate(self):
        self.config.write_json(self.table, "assets", "lang", self.lang_name+".json")

