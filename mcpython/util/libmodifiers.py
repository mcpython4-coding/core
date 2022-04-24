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
from bytecodemanipulation.MutableCodeObject import MutableCodeObject
from bytecodemanipulation.util import Opcodes
from mcpython import shared
from mcpython.engine import logger
import opcode


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
    method = MutableCodeObject.from_function(PIL.Image.Image.resize)

    # Security checks so mixin does only apply where it should
    assert method.code_string[30] == Opcodes.LOAD_ATTR, opcode.opname[method.code_string[30]]
    assert method.code_string[31] == 3, method.code_string[31]

    method.code_string[31] = method.ensureName(
        "NEAREST"
    )  # LOAD_GLOBAL BICUBIC -> NEAREST
    method.applyPatches()


def patchAsyncSystem():
    import asyncio.proactor_events

    method = MutableCodeObject.from_function(
        asyncio.proactor_events.BaseProactorEventLoop.close
    )


def removeLaunchWrapperPyVersionCheck():
    """
    Util method to be invoked by the launcher to disable the python version checker on launch.
    This is needed as the launcher may decide to use a newer python version than we have support for.
    """

    logger.println("[MIXIN][INFO] applying mixin to python version checker")
    import mcpython.LaunchWrapper

    method = MutableCodeObject.from_function(
        mcpython.LaunchWrapper.LaunchWrapper.check_py_version
    )

    method.code_string[0] = 100  # LOAD_CONST
    method.code_string[1] = 0  # None
    method.code_string[2] = 83  # return value
    method.code_string[3] = 0

    method.applyPatches()


patchAsyncSystem()


if shared.IS_CLIENT:
    applyPillowPatches()
