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
import sys
import types
from types import CodeType, FunctionType

__all__ = ["FunctionPatcher"]

import typing


def null():
    pass


class FunctionPatcher:
    """
    Code inspired by https://rushter.com/blog/python-bytecode-patch/

    Wrapped class for handling __code__ objects at runtime,
    and writing the modified code back into the source function

    See https://docs.python.org/3.10/library/inspect.html

    todo: add different wrapper types for different versions
    """

    def __init__(self, target: FunctionType):
        self.target = target
        self.code = self.target.__code__

        # Number of real arguments, neither positional only nor keyword arguments
        self.argument_count = self.code.co_argcount

        self.positional_only_argument_count = self.code.co_posonlyargcount
        self.keyword_only_argument_count = self.code.co_kwonlyargcount
        self.number_of_locals = self.code.co_nlocals
        self.max_stack_size = self.code.co_stacksize

        # Code flags, see https://docs.python.org/3.10/library/inspect.html#inspect-module-co-flags
        self.flags = self.code.co_flags

        # The code string, transformed to a bytearray for manipulation
        self.code_string = bytearray(self.code.co_code)

        # The constants in the code, use ensureConstant when wanting new ones
        self.constants = list(self.code.co_consts)

        # The local variable name table
        self.names = list(self.code.co_names)
        self.variable_names = list(self.code.co_varnames)
        self.filename = self.code.co_filename
        self.name = self.code.co_name
        self.first_line_number = self.code.co_firstlineno
        self.line_number_table = self.code.co_lnotab
        self.free_vars = self.code.co_freevars
        self.cell_vars = self.code.co_cellvars

        if sys.version_info.minor >= 11:
            self.columntable = self.code.co_columntable
            self.exceptiontable = self.code.co_exceptiontable
            self.end_line_table = self.code.co_endlinetable
            self.qual_name = self.code.co_qualname

    if sys.version_info.minor == 10:

        def applyPatches(self):
            """
            Writes the data this container holds back to the function
            """

            self.target.__code__ = CodeType(
                self.argument_count,
                self.positional_only_argument_count,
                self.keyword_only_argument_count,
                self.number_of_locals,
                self.max_stack_size,
                self.flags,
                bytes(self.code_string),
                tuple(self.constants),
                tuple(self.names),
                tuple(self.variable_names),
                self.filename,
                self.name,
                self.first_line_number,
                self.line_number_table,
                self.free_vars,
                self.cell_vars,
            )

    elif sys.version_info.minor == 11:

        def applyPatches(self):
            """
            Writes the data this container holds back to the function

            code_new_impl(PyTypeObject *type, int argcount, int posonlyargcount,
              int kwonlyargcount, int nlocals, int stacksize, int flags,
              PyObject *code, PyObject *consts, PyObject *names,
              PyObject *varnames, PyObject *filename, PyObject *name,
              PyObject *qualname, int firstlineno, PyObject *linetable,
              PyObject *endlinetable, PyObject *columntable,
              PyObject *exceptiontable, PyObject *freevars,
              PyObject *cellvars);
            """

            self.target.__code__ = CodeType(
                self.argument_count,
                self.positional_only_argument_count,
                self.keyword_only_argument_count,
                self.number_of_locals,
                self.max_stack_size,
                self.flags,
                bytes(self.code_string),
                tuple(self.constants),
                tuple(self.names),
                tuple(self.variable_names),
                self.filename,
                self.name,
                self.qual_name,
                self.first_line_number,
                self.line_number_table,
                self.end_line_table,
                self.columntable,
                self.exceptiontable,
                self.free_vars,
                self.cell_vars,
            )

    else:
        raise RuntimeError()

    def create_method_from(self):
        return FunctionType(
            CodeType(
                self.argument_count,
                self.positional_only_argument_count,
                self.keyword_only_argument_count,
                self.number_of_locals,
                self.max_stack_size,
                self.flags,
                bytes(self.code_string),
                tuple(self.constants),
                tuple(self.names),
                tuple(self.variable_names),
                self.filename,
                self.name,
                self.first_line_number,
                self.line_number_table,
                self.free_vars,
                self.cell_vars,
            ),
            globals(),
        )

    def overrideFrom(self, patcher: "FunctionPatcher"):
        """
        Force-overrides the content of this patcher with the one from another one
        """
        self.argument_count = patcher.argument_count
        self.positional_only_argument_count = patcher.positional_only_argument_count
        self.keyword_only_argument_count = patcher.keyword_only_argument_count
        self.number_of_locals = patcher.number_of_locals
        self.max_stack_size = patcher.max_stack_size
        self.flags = patcher.flags
        self.code_string = patcher.code_string
        self.constants = patcher.constants
        self.names = patcher.names
        self.variable_names = patcher.variable_names
        self.first_line_number = patcher.first_line_number
        self.line_number_table = patcher.line_number_table
        self.free_vars = patcher.free_vars
        self.cell_vars = patcher.cell_vars
        return self

    def copy(self):
        """
        Creates a copy of this object WITHOUT method binding
        """
        return FunctionPatcher(null).overrideFrom(self)

    def ensureConstant(self, const) -> int:
        """
        Makes some constant arrival in the program
        :param const: the constant
        :return: the index into the constant table
        """

        if const in self.constants:
            return self.constants.index(const)

        self.constants.append(const)
        return len(self.constants) - 1

    def get_instruction_list(self) -> typing.List[dis.Instruction]:
        return dis._get_instructions_bytes(
            self.code_string,
            self.variable_names,
            self.names,
            self.constants,
            self.cell_vars + self.free_vars,
        )

    def instructionList2Code(self, instruction_list: typing.List[dis.Instruction]):
        self.code_string.clear()

        for instr in instruction_list:
            try:
                self.code_string.append(instr.opcode)

                if instr.arg is not None:
                    self.code_string.append(instr.arg)
                else:
                    self.code_string.append(0)

            except:
                print(instr)
                raise

    def ensure_name(self, name: str) -> int:
        if name in self.names:
            return self.names.index(name)

        self.names.append(name)
        return len(self.names) - 1
