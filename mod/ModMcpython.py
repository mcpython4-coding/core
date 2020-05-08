"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

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

