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
from mcpython import shared
from mcpython.engine import logger
from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

if shared.IS_CLIENT:
    import PIL.Image

    logger.println(
        "[MIXIN][INFO] applying mixin to default resize() value of PIL.Image.Image.resize()..."
    )
    method = FunctionPatcher(PIL.Image.Image.resize)

    # Security checks so mixin does only apply where it should
    assert method.code_string[26] == 116
    assert method.code_string[27] == 2

    method.code_string[27] = 1  # LOAD_GLOBAL BICUBIC -> NEAREST
    method.applyPatches()
