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
from types import CodeType, FunctionType

__all__ = ["FunctionPatcher"]


class FunctionPatcher:
    """
    Code inspired by https://rushter.com/blog/python-bytecode-patch/

    Wrapped class for handling __code__ objects at runtime,
    and writing the modified code back into the source function
    """

    def __init__(self, target: FunctionType):
        self.target = target
        self.code = self.target.__code__

        self.argument_count = self.code.co_argcount
        self.positional_only_argument_count = self.code.co_posonlyargcount
        self.keyword_only_argument_count = self.code.co_kwonlyargcount
        self.number_of_locals = self.code.co_nlocals
        self.max_stack_size = self.code.co_stacksize
        self.flags = self.code.co_flags
        self.code_string = bytearray(self.code.co_code)
        self.constants = self.code.co_consts
        self.names = self.code.co_names
        self.variable_names = self.code.co_varnames
        self.filename = self.code.co_filename
        self.name = self.code.co_name
        self.first_line_number = self.code.co_firstlineno
        self.line_number_table = self.code.co_lnotab
        self.free_vars = self.code.co_freevars
        self.cell_vars = self.code.co_cellvars

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
            self.constants,
            self.names,
            self.variable_names,
            self.filename,
            self.name,
            self.first_line_number,
            self.line_number_table,
            self.free_vars,
            self.cell_vars,
        )
