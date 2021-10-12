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
import enum
import types
import typing

from mcpython import shared


def onlyInClient() -> typing.Callable:
    """
    Marks an object to be only arrival on the client, not on the server
    """
    if shared.IS_CLIENT:
        return lambda a: a
    else:

        def annotate(obj):
            if isinstance(obj, types.FunctionType):

                def replace(*_, **__):
                    raise NotImplementedError(obj, _, __)

                return replace

            else:

                class Replacement:
                    pass

                return Replacement

        return annotate
