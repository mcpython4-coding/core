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
import bytecodemanipulation

from mcpython import shared


async def optimise_annotated():
    bytecodemanipulation.OptimiserAnnotations.run_optimisations()


if not shared.IS_TEST_ENV:
    shared.mod_loader("minecraft", "stage:mixin:optimise_code")(optimise_annotated())

