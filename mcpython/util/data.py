"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

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
        raise ValueError("could not convert {}".format(data))
