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
import mcpython.common.config
import mcpython.common.mod.Mod
from mcpython import shared

VERSION_POST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# create the mod
mcpython = minecraft = mcpython.common.mod.Mod.Mod(
    "minecraft",
    (mcpython.common.config.VERSION_ID,),
    version_name=mcpython.common.config.VERSION_NAME,
)

if not shared.IS_TEST_ENV:
    mcpython.add_load_default_resources()


async def init():
    import mcpython.common.data.serializer.loot.LootTable
    import mcpython.common.entity.EntityManager


mcpython.eventbus.subscribe("stage:mod:init", init())
