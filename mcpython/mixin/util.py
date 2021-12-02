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
import dis
import typing


def create_instruction(
    opname_or_code: str | int,
    arg_pt: int = 0,
    arg_val: typing.Any = None,
    offset=-1,
    start_line=None,
    is_jump_target=False,
):
    if isinstance(opname_or_code, str):
        opname = opname_or_code
        opcode = dis.opmap[opname]
    else:
        opcode = opname_or_code
        opname = dis.opname[opcode]

    return dis.Instruction(
        opname, opcode, arg_pt, arg_val, arg_val, offset, start_line, is_jump_target
    )
