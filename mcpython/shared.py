"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import os, sys, tempfile

# todo: create MCPYTHON-class (as main game class) replacing this mess

invalidate_cache = "--invalidate-cache" in sys.argv
debug_events = "--debug-events" in sys.argv
dev_environment = True  # dynamical set on build

local = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
home = (
    local + "/home"
    if "--home-folder" not in sys.argv
    else sys.argv[sys.argv.index("--home-folder") + 1]
)
build = (
    home + "/build"
    if "--build-folder" not in sys.argv
    else sys.argv[sys.argv.index("--build-folder") + 1]
)
tmp = tempfile.TemporaryDirectory()

data_gen = (
    "--data-gen" in sys.argv or "--invalidate-cache" in sys.argv
) and dev_environment
data_gen_exit = "--exit-after-data-gen" in sys.argv  # default vanilla behaviour

STORAGE_VERSION = None  # the version of the storage format

window = None  # the window instance, client-only
world = None  # the world instance

chat = None  # the chat instance todo: migrate to player

event_handler = None  # the global event handler
tick_handler = None  # the global tick handler

registry = None  # the registry manager
command_parser = None  # the command parser
state_handler = None  # the state manager
inventory_handler = None  # the inventory manager instance
world_generation_handler = None  # the world generator manager instance
biome_handler = None  # the biome manger instance
crafting_handler = None  # the crafting manager instance
tag_handler = None  # the tag handler instance
dimension_handler = None  # the dimension handler instance
loot_table_handler = None  # the loot table manager instance
entity_handler = None  # the entity manager instance

model_handler = None  # the model handler instance, client-only

mod_loader = None  # the mod loader instance


# todo: move to separated file
import mcpython.client.rendering.RenderingHelper

rendering_helper = mcpython.client.rendering.RenderingHelper.RenderingHelper()

NEXT_EVENT_BUS_ID = 0
