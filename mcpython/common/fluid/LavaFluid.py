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
import mcpython.common.fluid.AbstractFluid


class LavaFluid(mcpython.common.fluid.AbstractFluid.AbstractFluid):
    # todo: more properties

    NAME = "minecraft:lava"

    IS_FINITE = True

    TEXTURE_FLOW: str = "minecraft:block/lava_flow"
    TEXTURE_STILL: str = "minecraft:block/lava_still"

    DEFAULT_FLUID_TEMPERATURE: float = 1403

    # Only for mods
    SOLIDIFICATION_POINT = 603
    SOLIDIFIES_TO = "minecraft:cobblestone"
