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
import opcode

from bytecodemanipulation.MutableFunction import Instruction
from bytecodemanipulation.MutableFunction import MutableFunction
from bytecodemanipulation.Opcodes import Opcodes
from mcpython import shared
from mcpython.engine import logger


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
    method = MutableFunction(PIL.Image.Image.resize)

    # Security checks so mixin does only apply where it should
    assert method.instructions[15] == Instruction(method, 15, Opcodes.LOAD_ATTR, "BICUBIC"), method.instructions[15]

    method.instructions[15].change_arg_value("NEAREST")
    method.reassign_to_function()


def patchAsyncSystem():
    import asyncio.proactor_events

    method = MutableFunction(
        asyncio.proactor_events.BaseProactorEventLoop.close
    )


def removeLaunchWrapperPyVersionCheck():
    """
    Util method to be invoked by the launcher to disable the python version checker on launch.
    This is needed as the launcher may decide to use a newer python version than we have support for.
    """

    logger.println("[MIXIN][INFO] applying mixin to python version checker")
    import mcpython.LaunchWrapper

    method = MutableFunction(
        mcpython.LaunchWrapper.LaunchWrapper.check_py_version
    )

    method.instructions[0] = Instruction(method, 0, Opcodes.LOAD_CONST, None)
    method.instructions[1] = Instruction(method, 1, Opcodes.RETURN_VALUE, None)

    method.reassign_to_function()


patchAsyncSystem()


if shared.IS_CLIENT:
    applyPillowPatches()
