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
from mcpython import shared
from mcpython.common.data.gen.DataGeneratorManager import DataGeneratorInstance
from mcpython.common.data.gen.TextureDataGen import TextureConstructor

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
