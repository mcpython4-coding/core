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
import marshal
import types

GLOBAL = globals()

exec(
    """
import time, os, asyncio
""",
    GLOBAL,
)


def serialize_task(function, args, kwargs, meta=None):
    return marshal.dumps(function.__code__), args, kwargs, meta


def deserialize_task(data):
    return (types.FunctionType(marshal.loads(data[0]), GLOBAL),) + data[1:]
