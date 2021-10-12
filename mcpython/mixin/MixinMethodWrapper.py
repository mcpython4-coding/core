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
import functools
import typing

from mcpython.engine import logger
from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher


def reconstruct_instruction(
    instr: dis.Instruction,
    arg=None,
    arg_value=None,
    arg_repr=None,
    offset=None,
    jump_target=None,
):
    return dis.Instruction(
        instr.opname,
        instr.opcode,
        arg or instr.arg,
        arg_value or instr.argval,
        arg_repr or instr.argrepr,
        offset or instr.offset,
        instr.starts_line,
        jump_target or instr.is_jump_target,
    )


def mixin_return(value=None):
    """
    Invoke before a normal return in a mixin injected to return the method injected into
    This method call and the return will be combined into a regular return statement
    """


def capture_local(name: str):
    """
    Invoke in a mixin injected method to get a local variable by name from the outer method
    Will optimise into a load_fast call
    """


OFFSET_JUMPS = ("JUMP_FORWARD", "FOR_ITER", "SETUP_FINALLY")
REAL_JUMPS = (
    "POP_JUMP_IF_TRUE",
    "POP_JUMP_IF_FALSE",
    "JUMP_IF_NOT_EXC_MATCH",
    "JUMP_IF_TRUE_OR_POP",
    "JUMP_IF_FALSE_OR_POP",
    "JUMP_ABSOLUTE",
)


class MixinPatchHelper:
    """
    See https://docs.python.org/3/library/dis.html#python-bytecode-instructions for a detailed instruction listing
    Contains helper methods for working with bytecode outside the basic wrapper
    """

    def __init__(self, patcher: FunctionPatcher):
        self.patcher = patcher
        self.instruction_listing = list(self.patcher.get_instruction_list())

    def walk(self) -> typing.Iterable[typing.Tuple[int, dis.Instruction]]:
        yield from zip(range(len(self.instruction_listing)), self.instruction_listing)

    def store(self):
        self.patcher.instructionList2Code(self.instruction_listing)

    def deleteRegion(self, start: int, end: int, safety=True):
        """
        Deletes a region from start (including) to end (excluding) of the code, rebinding jumps and similar calls
        outside the region
        If safety is True, will ensure no direct jumps occur in this region
        """
        i = 0
        size = end - start

        def rebind_offset(o: int) -> int:
            nonlocal i

            if start <= i + o < end and safety:
                raise RuntimeError("instruction to jump to is getting deleted")

            # If we jump OVER the region
            if i + o >= end and i < start:
                return o - size

            if i + o < start and i >= end:
                return o + size

            return o

        def rebind_real(o: int) -> int:
            if start <= o < end and safety:
                raise RuntimeError("instruction to jump to is getting deleted")

            if o >= end:
                return o - size

            return o

        for i, instr in self.walk():
            if start <= i < end:
                continue

            # Check control flow
            if instr.opname in OFFSET_JUMPS:
                offset = instr.arg
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_offset(offset)
                )

            elif instr.opname in REAL_JUMPS:
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_real(instr.arg)
                )

        del self.instruction_listing[start:end]

    def insertRegion(self, start: int, instructions: typing.List[dis.Instruction]):
        """
        Inserts a list of instructions into the opcode list, resolving the jumps in code correctly
        """
        size = len(instructions)

        def rebind_offset(o: int) -> int:
            nonlocal i

            # If we jump OVER the region
            if i + o >= start > i:
                return o + size

            if i + o < start <= i:
                return o - size

            return o

        def rebind_real(o: int) -> int:

            # If we jump OVER the region
            if o >= start:
                return o - size

            return o

        for i, instr in self.walk():
            # Check control flow
            if instr.opname in OFFSET_JUMPS:
                offset = instr.arg
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_offset(offset)
                )

            elif instr.opname in REAL_JUMPS:
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_real(instr.arg)
                )

        self.instruction_listing = (
            self.instruction_listing[: start - 1]
            + instructions
            + self.instruction_listing[start - 1 :]
        )

    def insertMethodAt(self, start: int, method: FunctionPatcher):
        """
        Inserts a method body at the given position
        Does some magic for linking the code
        Use mixin_return or capture_local for advance control flow

        Will not modify the passed method. Will copy that object
        """
        method = self.prepare_method_for_insert(method)

    def insertMethodMultipleTimesAt(
        self,
        start: typing.List[int],
        method: FunctionPatcher,
        force_multiple_inlines=False,
    ):
        pass

    def insertStaticMethodCallAt(self, offset: int, method: str, *args):
        module, path = method.split(":")
        real_name = path.split(".")[-1]

        if path.count(".") > 0:
            real_module = module + "." + ".".join(path.split(".")[:-1])
        else:
            real_module = module

        instructions = [
            dis.Instruction(
                "LOAD_CONST",
                100,
                self.patcher.ensureConstant(0),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "LOAD_CONST",
                100,
                self.patcher.ensureConstant((real_name,)),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "IMPORT_NAME",
                108,
                self.patcher.ensure_name(real_module),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "IMPORT_FROM",
                109,
                self.patcher.ensure_name(real_name),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "STORE_FAST",
                125,
                self.patcher.ensure_name(real_module),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "POP_TOP",
                1,
                None,
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "LOAD_FAST",
                124,
                self.patcher.ensure_name(real_module),
                None,
                None,
                False,
                0,
                0.0,
            ),
        ]

        for arg in args:
            instructions.append(
                dis.Instruction(
                    "LOAD_CONST",
                    100,
                    self.patcher.ensureConstant(arg),
                    None,
                    None,
                    False,
                    0,
                    0,
                )
            )

        instructions += [
            dis.Instruction(
                "CALL_FUNCTION",
                131,
                len(args),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "POP_TOP",
                1,
                0,
                None,
                None,
                False,
                0,
                0,
            ),
        ]

        self.patcher.max_stack_size += max(2, len(args))
        self.patcher.number_of_locals += 1
        self.patcher.variable_names.append(real_name)

        self.insertRegion(
            offset,
            instructions,
        )

    @staticmethod
    def prepare_method_for_insert(method: FunctionPatcher) -> FunctionPatcher:
        """
        Prepares a FunctionPatcher for being inserted into another method
        Does the stuff around the control flow control methods
        Will work on a copy of the method, not the method itself
        """
        breakpoint()
        method = method.copy()

        i = 0
        helper = MixinPatchHelper(method)

        while i < len(helper.instruction_listing):
            instr = helper.instruction_listing[i]

        return method
