"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G

config = {"layers": ["landmass_default", "temperaturemap", "biomemap_default", "highmap_default", "bedrock_default",
                     "stone_default", "toplayer_default"]}

G.worldgenerationhandler.register_world_gen_config("default_overworld", config)

