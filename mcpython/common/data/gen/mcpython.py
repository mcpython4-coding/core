"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython.common.data.gen.TextureDataGen import TextureConstructor
from mcpython.common.data.gen.DataGeneratorManager import DataGeneratorInstance
from mcpython import shared


generator = DataGeneratorInstance(
    shared.local + "/resources/generated" if shared.dev_environment else shared.local
)

generator.annotate(
    TextureConstructor("chest_gui")
    .add_image_layer_top("minecraft:gui/container/shulker_box")
    .crop((0, 0, 176 / 255, 166 / 255))
    .scaled((2, 2)),
    "assets/minecraft/textures/gui/chest_gui_generated.png",
)
generator.annotate(
    TextureConstructor("crafting_table_gui")
    .add_image_layer_top("minecraft:gui/container/crafting_table")
    .crop((0, 0, 176 / 255, 166 / 255))
    .scaled((2, 2)),
    "assets/minecraft/textures/gui/crafting_table_generated.png",
)
