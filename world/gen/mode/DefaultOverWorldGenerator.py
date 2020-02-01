"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G

config = {"layers": ["landmass_default", "temperaturemap", "biomemap_default", "heightmap_default", "bedrock_default",
                     "stone_default", "toplayer_default", "tree_default"]}

G.worldgenerationhandler.register_world_gen_config("default_overworld", config)

