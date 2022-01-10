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
# Now, this is strange, we do mix into our own code???
# So, this optimises some code invoked often on client / server, which has client / server checks

import mcpython.mixin.Mixin
from mcpython import shared
from mcpython.mixin.Mixin import mixin_handler

if shared.IS_CLIENT:

    @shared.mod_loader("minecraft", "stage:mixin:prepare")
    def optimise():
        mixin_handler.replace_attribute_with_constant(
            "mcpython.common.event.TickHandler:TickHandler.tick", "IS_CLIENT", True
        )


else:

    @shared.mod_loader("minecraft", "stage:mixin:prepare")
    def optimise():
        mixin_handler.replace_attribute_with_constant(
            "mcpython.common.event.TickHandler:TickHandler.tick", "IS_CLIENT", False
        )
