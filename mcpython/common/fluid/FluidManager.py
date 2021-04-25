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
import mcpython.common.event.Registry
import mcpython.common.fluid.AbstractFluid
from mcpython import shared


fluid_manager = mcpython.common.event.Registry.Registry(
    "minecraft:fluid", ["minecraft:fluid"], "stage:fluids:register"
)


@shared.mod_loader("minecraft", "stage:fluids:register")
def register_fluids():
    from . import LavaFluid, WaterFluid

    fluid_manager.register(LavaFluid.LavaFluid)
    fluid_manager.register(WaterFluid.WaterFluid)
