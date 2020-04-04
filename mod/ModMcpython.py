"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mod.Mod
import config

VERSION_POST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

VERSION = (0, 1, int(config.VERSION_NAME[:2]), int(config.VERSION_NAME[3:5]),
           VERSION_POST.index(config.VERSION_NAME[5]))

# create the mod
mcpython = mod.Mod.Mod("minecraft", VERSION)


def init():
    import loot.LootTable
    import entity.EntityHandler


mcpython.eventbus.subscribe("stage:mod:init", init)

