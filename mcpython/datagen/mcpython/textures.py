"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from mcpython.datagen import Configuration
from mcpython.datagen.TextureDataGen import TextureConstructor
import sys

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment


@G.modloader("minecraft", "special:datagen:configure")
def load_block_states():
    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    config = Configuration.DataGeneratorConfig("minecraft", G.local + "/resources/generated")
    config.setDefaultNamespace("minecraft")

    for wood_type in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]:
        TextureConstructor(config, "block/{}_leaves".format(wood_type), (16, 16)).add_coloring_layer(
            "minecraft:block/{}_leaves".format(wood_type), (201, 248, 153))

