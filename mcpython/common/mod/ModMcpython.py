"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.mod.Mod
import mcpython.common.config
from mcpython import logger

VERSION_POST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parse_version(string: str) -> tuple:
    if type(string) == str and string[2] == "w":  # snapshot
        # type - alpha (0), pre - 1, post - 2, point - 0, a, b, c, build
        return 0, 1, 1, 0, int(string[:2]), int(string[3:5]), VERSION_POST.index(string[5]), mcpython.common.config.DEVELOPMENT_COUNTER
    elif type(string) == str:
        if string.startswith("snapshot dev "):
            previous = parse_version(mcpython.common.config.DEVELOPING_FOR)
            return previous[:-1] + (mcpython.common.config.DEVELOPMENT_COUNTER,)
        else:  # format: [type][a].[b].[c]
            c = string[1:].split(".")
            return "abr".index(string[0]), int(c[0]), int(c[1]), int(c[2]), mcpython.common.config.DEVELOPMENT_COUNTER
    else:
        logger.println("[WARN] version entry {} wrong formatted".format(string))
        return tuple(string.split("."))


# create the mod
mcpython = mcpython.common.mod.Mod.Mod("minecraft", parse_version(mcpython.common.config.VERSION_NAME))


def init():
    pass


mcpython.eventbus.subscribe("stage:mod:init", init)

