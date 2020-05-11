"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mod.Mod
import config
import logger

VERSION_POST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

if type(config.VERSION_NAME) == str and config.VERSION_NAME[2] == "w":  # snapshot
    VERSION = (0, 1, int(config.VERSION_NAME[:2]), int(config.VERSION_NAME[3:5]),
               VERSION_POST.index(config.VERSION_NAME[5]))
elif type(config.VERSION_NAME) == str:
    if config.VERSION_NAME.startswith("snapshot dev "):
        s = config.VERSION_NAME.split(" ")
        VERSION = (0, 2, s[2], s[4])
    else:
        c = config.VERSION_NAME
        if c[0] in "abr": c = c[1:]
        VERSION = tuple([int(e) for e in c.split(".")])
else:
    logger.println("[WARN] version entry wrong formatted")
    VERSION = config.VERSION_NAME

# create the mod
mcpython = mod.Mod.Mod("minecraft", VERSION)


def init():
    import loot.LootTable
    import entity.EntityHandler


mcpython.eventbus.subscribe("stage:mod:init", init)

