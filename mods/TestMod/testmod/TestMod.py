import mod.Mod
import globals as G


minecraft = mod.Mod.Mod("testmod", "0.0.1")


def inject():  # special method called when system is ready for accepting these code
    # needed for enabling recipe loading for these mod
    import crafting.CraftingHandler
    minecraft.eventbus.subscribe("stage:recipes", G.craftinghandler.load, "testmod", info="loading crafting recipes")

# todo: add example block class, item class, crafting recipes


minecraft.eventbus.subscribe("stage:prepare", inject, info="adding event subscriptions")

