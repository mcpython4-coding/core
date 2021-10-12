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
import os
import sys
import tempfile

launch_wrapper = None

# todo: create MCPYTHON-class (as main game class) replacing this mess

invalidate_cache = "--invalidate-cache" in sys.argv
dev_environment = True  # dynamical set on build
NO_LOG_ESCAPE = "--no-log-escape" in sys.argv

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
if data_gen_exit and not data_gen:
    raise RuntimeError("could not --exit-after-data-gen and not --data-gen!")
NO_WINDOW = False

IS_CLIENT = True
IS_NETWORKING = False
IS_TEST_ENV = False

# Used by the mod loading system to store the name of the mod doing stuff currently
# Only updated when currently loading the game
CURRENT_EVENT_SUB = None

# The current mixin ref map, used by the JVM when needed
CURRENT_REF_MAP = None

STORAGE_VERSION = None  # the version of the storage format

# the window instance, client-only
window = None

# the chat instance, client only todo: migrate to player
chat = None

world = None  # the world instance

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
entity_manager = None  # the entity manager instance
capability_manager = None  # the capability manager instance

model_handler = None  # the model handler instance, client-only

mod_loader = None  # the mod loader instance


try:
    # todo: move to separated file
    # todo: do this only on the client!
    import mcpython.engine.rendering.RenderingHelper as _helper

    rendering_helper = _helper.RenderingHelper()
except ImportError:
    rendering_helper = None

NEXT_EVENT_BUS_ID = 0

CLIENT_NETWORK_HANDLER = None
SERVER_NETWORK_HANDLER = None
NETWORK_MANAGER = None

ENABLE_MOD_LOADER = True
ENABLE_DATAPACK_LOADER = True
ENABLE_RESOURCE_PACK_LOADER = True
