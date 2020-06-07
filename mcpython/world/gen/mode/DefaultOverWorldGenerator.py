"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G

config = {"layers": ["landmass_default", "temperaturemap", "biomemap_default", "heightmap_default", "bedrock_default",
                     "stone_default", "top_layer_default", "tree_default"]}

G.worldgenerationhandler.register_world_gen_config("default_overworld", config)
