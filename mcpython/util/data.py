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
import simplejson


def bytes_to_json(data: bytes):
    return simplejson.loads(data.decode("utf-8"))


def json_to_bytes(data: dict) -> bytes:
    return simplejson.dumps(data, indent="  ").encode("utf-8")


def lists_to_tuples(data, levels=-1):
    if levels == 0:
        return data
    if isinstance(data, dict):
        return {key: lists_to_tuples(data[key], levels - 1) for key in data}
    elif isinstance(data, list) or isinstance(data, tuple):
        return tuple([lists_to_tuples(entry, levels - 1) for entry in data])
    elif isinstance(data, set) or type(data) in (int, float, str, complex):
        return data
    else:
        raise ValueError("could not convert data {}".format(data))
