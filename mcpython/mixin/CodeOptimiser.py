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

from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
from mcpython.mixin.util import PyOpcodes

SIDE_EFFECT_FREE_VALUE_LOAD = {
    PyOpcodes.LOAD_FAST,
    PyOpcodes.LOAD_GLOBAL,
    PyOpcodes.LOAD_CONST,
    PyOpcodes.LOAD_DEREF,
    PyOpcodes.LOAD_CLASSDEREF,
    PyOpcodes.LOAD_NAME,
    PyOpcodes.LOAD_ASSERTION_ERROR,
    PyOpcodes.LOAD_BUILD_CLASS,
    PyOpcodes.LOAD_CLOSURE,
    PyOpcodes.LOAD_METHOD,
}


PAIR_LOAD_STORE = {
    PyOpcodes.LOAD_FAST: PyOpcodes.STORE_FAST,
    PyOpcodes.LOAD_GLOBAL: PyOpcodes.STORE_GLOBAL,
    PyOpcodes.LOAD_NAME: PyOpcodes.STORE_NAME,
    PyOpcodes.LOAD_DEREF: PyOpcodes.STORE_DEREF,
}

PAIR_STORE_DELETE = {
    PyOpcodes.STORE_FAST: PyOpcodes.DELETE_FAST,
    PyOpcodes.STORE_NAME: PyOpcodes.DELETE_NAME,
    PyOpcodes.STORE_GLOBAL: PyOpcodes.DELETE_GLOBAL,
    PyOpcodes.STORE_DEREF: PyOpcodes.DELETE_DEREF,
}


def optimise_code(helper: MixinPatchHelper):
    remove_store_delete_pairs(helper)
    remove_load_pop(helper)
    remove_load_store_pairs(helper)
    remove_delete_fast_without_assign(helper)
    remove_nop(helper)


# Optimise-able:
# constant + conditional jump -> unconditional jump / no code
# empty for_iter
# RAISE in a try-except block ignoring the exception or handling only the exception instance
# CALL_FUNCTION to a side effect free method followed by a POP_TOP
# CALL_FUNCTION_KW to a side effect free method followed by a POP_TOP
# MAKE_FUNCTION directly popped from the stack
# is_constant() marker for function calls, together with local type hints
# side effect free popped math operation (Value check / value type hint)
# Single/more-accessed STORE_XX in a following region which can be served via the stack

# todo: track LOAD_XX better, depending on context, we may have some other instructions in between,
#   but we can optimise these instructions away


def remove_store_delete_pairs(helper: MixinPatchHelper):
    """
    Optimiser method for removing side effect free STORE_XX instructions directly followed by a
    DELETE_XX instruction.
    Refactors it into a POP_TOP followed by a DELETE_XX

    The POP_TOP instruction than can be optimised away by the remove_load_pop() optimiser if possible.
    The DELETE_XX instruction can be optimised away by the remove_delete_fast_without_assign() optimiser if possible.
    """
    index = -1
    while index < len(helper.instruction_listing) - 1:
        index += 1
        for index, instr in list(helper.walk())[index:]:
            if (
                instr.opcode in PAIR_STORE_DELETE
                and index < len(helper.instruction_listing) - 2
            ):
                next_instr = helper.instruction_listing[index + 1]
                if (
                    next_instr.opcode == PAIR_STORE_DELETE[instr.opcode]
                    and instr.arg == next_instr.arg
                ):
                    # Delete the load instruction and the store instruction
                    helper.instruction_listing[index] = dis.Instruction(
                        "POP_TOP",
                        PyOpcodes.POP_TOP,
                        0,
                        0,
                        "",
                        0,
                        0,
                        False,
                    )
                    break
        else:
            break


def remove_delete_fast_without_assign(helper: MixinPatchHelper):
    """
    Removes all DELETE_FAST instructions deleting locals not written to yet
    This is an artifact left by other optimisation functions
    """
    # the arguments are written to, but anything else is not
    written_to = set(range(helper.patcher.argument_count))

    index = -1
    while index < len(helper.instruction_listing) - 1:
        index += 1
        for index, instr in list(helper.walk())[index:]:
            if instr.opcode == PyOpcodes.STORE_FAST:
                written_to.add(instr.arg)

            elif instr.opcode == PyOpcodes.DELETE_FAST and instr.arg not in written_to:
                helper.deleteRegion(index, index + 1)
                index -= 1
                break
        else:
            break


def remove_load_pop(helper: MixinPatchHelper):
    """
    Optimiser method for removing side effect free LOAD_XX instructions directly followed by a
    POP_TOP instruction
    """
    index = -1
    while index < len(helper.instruction_listing) - 1:
        index += 1
        for index, instr in list(helper.walk())[index:]:
            if instr.opcode == PyOpcodes.POP_TOP and index > 0:
                previous = helper.instruction_listing[index - 1]
                if previous.opcode in SIDE_EFFECT_FREE_VALUE_LOAD:
                    # Delete the side effect free result and the POP_TOP instruction
                    helper.deleteRegion(index - 1, index + 1)
                    index -= 2
                    break
        else:
            break


def remove_load_store_pairs(helper: MixinPatchHelper):
    """
    Optimiser method for removing side effect free LOAD_XX followed by STORE_XX to the same space

    Removing e.g. a = a in the process
    """

    index = -1
    while index < len(helper.instruction_listing) - 1:
        index += 1
        for index, instr in list(helper.walk())[index:]:
            if (
                instr.opcode in PAIR_LOAD_STORE
                and index < len(helper.instruction_listing) - 2
            ):
                next_instr = helper.instruction_listing[index + 1]
                if (
                    next_instr.opcode == PAIR_LOAD_STORE[instr.opcode]
                    and instr.arg == next_instr.arg
                ):
                    # Delete the load instruction and the store instruction
                    helper.deleteRegion(index, index + 2)
                    index -= 1
                    break
        else:
            break


def remove_nop(helper: MixinPatchHelper):
    """
    Optimiser method for removing NOP instructions
    todo: can we combine-delete multiple instructions?
    """

    index = -1
    while index < len(helper.instruction_listing) - 1:
        index += 1
        for index, instr in list(helper.walk())[index:]:
            if instr.opcode == PyOpcodes.NOP:
                helper.deleteRegion(index, index + 1, maps_invalid_to=index)
                index -= 1
                break
        else:
            break