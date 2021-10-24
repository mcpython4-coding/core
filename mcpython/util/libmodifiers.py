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


def applyPillowPatches():
    try:
        import PIL.Image
    except (ImportError, ModuleNotFoundError):
        logger.println(
            "[MIXIN][INFO] failed to apply mixin to default resize() value of PIL.Image.Image.resize(), PIL not found!"
        )
        return

    logger.println(
        "[MIXIN][INFO] applying mixin to default resize() value of PIL.Image.Image.resize()..."
    )
    method = FunctionPatcher(PIL.Image.Image.resize)

    # Security checks so mixin does only apply where it should
    assert method.code_string[26] == 116
    assert method.code_string[27] == 2

    method.code_string[27] = 1  # LOAD_GLOBAL BICUBIC -> NEAREST
    method.applyPatches()


def removeLaunchWrapperPyVersionCheck():
    """
    Util method to be invoked by the launcher to disable the python version checker on launch.
    This is needed as the launcher may decide to use a newer python version than we have support for.
    """

    logger.println("[MIXIN][INFO] applying mixin to python version checker")
    import mcpython.LaunchWrapper

    method = FunctionPatcher(mcpython.LaunchWrapper.LaunchWrapper.check_py_version)

    method.code_string[0] = 100  # LOAD_CONST
    method.code_string[1] = 0  # None
    method.code_string[2] = 83  # return value
    method.code_string[3] = 0

    method.applyPatches()


if shared.IS_CLIENT:
    applyPillowPatches()
