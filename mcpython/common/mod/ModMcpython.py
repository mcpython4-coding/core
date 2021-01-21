"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.mod.Mod
import mcpython.common.config
from mcpython import logger

VERSION_POST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# create the mod
mcpython = mcpython.common.mod.Mod.Mod(
    "minecraft",
    (mcpython.common.config.VERSION_ID,),
    version_name=mcpython.common.config.VERSION_NAME,
)
mcpython.add_load_default_resources()


def init():
    import mcpython.common.data.loot.LootTable
    import mcpython.common.entity.EntityHandler


mcpython.eventbus.subscribe("stage:mod:init", init)
