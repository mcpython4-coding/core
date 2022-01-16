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
import traceback
import types
import typing

from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

from .util import PyOpcodes


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

    Use from <...>.MixinMethodWrapper import mixin_return outside the method in a global scope when possible,
    it makes it easier to detect inside the bytecode

    todo: use this for real!
    """


def capture_local(name: str):
    """
    Captures the value from an outer local variable into this function body.
    Use only in mixin injected (real injection) code!

    WARNING: when storing the result in a local variable, the name of the variable is captured
    in the whole function, meaning any read/write to this name will be redirected to the real local
    variable; This can result in unwanted side effects

    :param name: the name of the local
    :return: the local value
    """


# todo: add a way to capture free variables
# todo: add a way to capture global variables
# todo: add a way to capture cell variables


OFFSET_JUMPS = dis.hasjrel
REAL_JUMPS = dis.hasjabs
LOAD_SINGLE_VALUE = {
    PyOpcodes.LOAD_FAST,
    PyOpcodes.LOAD_CONST,
    PyOpcodes.LOAD_DEREF,
    PyOpcodes.LOAD_GLOBAL,
    PyOpcodes.LOAD_BUILD_CLASS,
    PyOpcodes.LOAD_NAME,
    PyOpcodes.LOAD_CLASSDEREF,
}
POP_SINGLE_VALUE = {
    PyOpcodes.STORE_FAST,
    PyOpcodes.STORE_DEREF,
    PyOpcodes.STORE_GLOBAL,
    PyOpcodes.STORE_NAME,
}
POP_DOUBLE_VALUE = {
    PyOpcodes.STORE_ATTR,
    PyOpcodes.STORE_SUBSCR,
}
POP_DOUBLE_AND_PUSH_SINGLE = {
    PyOpcodes.STORE_SUBSCR,
    PyOpcodes.STORE_ATTR,
}
POP_SINGLE_AND_PUSH_SINGLE = {
    PyOpcodes.LOAD_METHOD,
}


class MixinPatchHelper:
    """
    See https://docs.python.org/3/library/dis.html#python-bytecode-instructions for a detailed instruction listing
    Contains helper methods for working with bytecode outside the basic wrapper container

    Can save-ly exchange code regions with others, and redirect jump instructions correctly.

    Also contains code to inline whole methods into the code
    """

    def __init__(self, patcher: FunctionPatcher | types.FunctionType):
        self.patcher = (
            patcher
            if isinstance(patcher, FunctionPatcher)
            else FunctionPatcher(patcher)
        )
        self.instruction_listing = list(self.patcher.get_instruction_list())
        self.is_async = self.instruction_listing[0].opname == "GEN_START"

    def walk(self) -> typing.Iterable[typing.Tuple[int, dis.Instruction]]:
        yield from zip(range(len(self.instruction_listing)), self.instruction_listing)

    def store(self):
        self.patcher.instructionList2Code(self.instruction_listing)
        self.instruction_listing[:] = list(self.patcher.get_instruction_list())

    def re_eval_instructions(self):
        self.store()
        self.instruction_listing[:] = list(self.patcher.get_instruction_list())

    def deleteRegion(self, start: int, end: int, safety=True):
        """
        Deletes a region from start (including) to end (excluding) of the code, rebinding jumps and similar calls
        outside the region
        If safety is True, will ensure no direct jumps occur into this region
        (This is done during code walking for jump resolving)

        WARNING: the user is required to make sure that stack & variable constraints still hold
        """
        i = 0
        size = end - start

        def rebind_offset(o: int) -> int:
            nonlocal i

            if start <= i + o < end and safety:
                raise RuntimeError("Instruction to jump to is getting deleted")

            # If we jump OVER the region
            if i + o >= end and i < start:
                return o - size

            if i + o < start and i >= end:
                return o + size

            return o

        def rebind_real(o: int) -> int:
            if start <= o < end and safety:
                raise RuntimeError("Instruction to jump to is getting deleted")

            if o >= end:
                return o - size

            return o

        for i, instr in self.walk():
            if start <= i < end:
                continue

            # Check control flow
            if instr.opcode in OFFSET_JUMPS:
                offset = instr.arg
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_offset(offset)
                )

            elif instr.opcode in REAL_JUMPS:
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_real(instr.arg)
                )

        del self.instruction_listing[start:end]

    def insertRegion(self, start: int, instructions: typing.List[dis.Instruction]):
        """
        Inserts a list of instructions into the opcode list, resolving the jumps in code correctly

        WARNING: the user is required to make sure that stack & variable constraints still hold
        """
        start -= 1
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
            if instr.opcode in OFFSET_JUMPS:
                offset = instr.arg
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_offset(offset)
                )

            elif instr.opcode in REAL_JUMPS:
                self.instruction_listing[i] = reconstruct_instruction(
                    instr, arg=rebind_real(instr.arg)
                )

        self.instruction_listing = (
            self.instruction_listing[: start - 1]
            + instructions
            + self.instruction_listing[start - 1 :]
        )

    def deleteInstruction(self, instr: dis.Instruction):
        self.deleteRegion(instr.offset, instr.offset + 1)
        return self

    def replaceConstant(
        self,
        previous,
        new,
        matcher: typing.Callable[["MixinPatchHelper", int, int], bool] = None,
    ):
        """
        Replaces a constant with another one
        :param previous: the old constant
        :param new: the new constant
        :param matcher: the matcher for instructions, or None
        """
        if previous not in self.patcher.constants:
            raise ValueError(previous)

        if matcher is None:
            const_index = self.patcher.constants.index(previous)
            self.patcher.constants[const_index] = new
        else:
            const_index = self.patcher.ensureConstant(new)

        match = 0
        for index, instruction in enumerate(self.instruction_listing):
            if instruction.opcode in dis.hasconst:
                match += 1
                if instruction.arg == const_index and (
                    matcher is None or matcher(self, index, match)
                ):
                    self.instruction_listing[index] = dis.Instruction(
                        instruction.opname,
                        instruction.opcode,
                        const_index,
                        new,
                        repr(new),
                        instruction.offset,
                        instruction.starts_line,
                        instruction.is_jump_target,
                    )

    def getLoadGlobalsLoading(
        self, global_name: str
    ) -> typing.Iterable[typing.Tuple[int, dis.Instruction]]:
        for index, instruction in enumerate(self.instruction_listing):
            if (
                instruction.opname == "LOAD_GLOBAL"
                and instruction.argval == global_name
            ):
                yield index, instruction

    def insertMethodAt(
        self,
        start: int,
        method: FunctionPatcher | types.MethodType,
        force_inline=True,
        added_args=0,
        discard_return_result=True,
    ):
        """
        Inserts a method body at the given position
        Does some magic for linking the code
        Use mixin_return() or capture_local() for advance control flow

        Will not modify the passed method. Will copy that object

        All locals not capture()-ed get a new prefix of the method name

        WARNING: mixin_return() with arg the arg must be from local variable storage, as it is otherwise
            hard to detect where the method came from (LOAD_GLOBAL somewhere in instruction list...)
        todo: add a better way to trace function calls

        WARNING: highly experimental, it may break at any time!

        :param start: where the method head should be inserted
        :param method: the method object ot inject
        :param force_inline: forced a inline, currently always inlining code
        :param added_args: how many positional args are added to the method call
        :param discard_return_result: if the return result should be deleted or not
        """

        if not isinstance(method, FunctionPatcher):
            method = FunctionPatcher(method)

        target = method.copy()

        # Rebind all inner local variables to something we cannot possibly enter,
        # so we cannot get conflicts (in the normal case)
        target.variable_names = [
            method.target.__name__ + "::" + e for e in target.variable_names
        ]

        helper = MixinPatchHelper(target)

        # Rewire JUMP_ABSOLUTE instructions to the new offset
        for index, instr in helper.walk():
            if instr.opname == "JUMP_ABSOLUTE":
                helper.instruction_listing[index] = reconstruct_instruction(
                    instr, instr.arg + start
                )

        captured = {}
        captured_indices = set()
        captured_names = set()

        protect = set()

        # Walk across the code and look out of captures

        index = -1
        while index != len(helper.instruction_listing) - 1:
            index += 1
            for index, instr in list(helper.walk())[index:]:
                if instr.opname == "CALL_FUNCTION" and index > 1:
                    possible_load = helper.instruction_listing[index - 2]
                    if (
                        possible_load.opname in ("LOAD_GLOBAL", "LOAD_DEREF")
                        and possible_load.argval == "capture_local"
                    ):
                        assert (
                            helper.instruction_listing[index - 1].opname == "LOAD_CONST"
                        ), "captured must be local var"

                        local = helper.instruction_listing[index - 1].argval

                        if helper.instruction_listing[index + 1].opname == "STORE_FAST":
                            capture_target = helper.instruction_listing[
                                index + 1
                            ].argval

                            captured[
                                capture_target
                            ] = local, self.patcher.ensureVarName(local)
                            captured_indices.add(index)
                            captured_names.add(local)

                            # LOAD_<method> "capture_local"  {index-2}
                            # LOAD_CONST <local name>        {index-1}
                            # CALL_FUNCTION 1                {index+0}
                            # STORE_FAST <new local name>    {index+1}
                            helper.deleteRegion(index - 2, index + 2)

                            print(
                                f"found local variable access onto '{local}' from '{capture_target}' (var index: {self.patcher.ensureVarName(local)}) at {index} ({instr})"
                            )
                            index -= 1

                        # We don't really know what is done to the local,
                        # so we need to store it as
                        else:
                            captured_names.add(local)

                            # LOAD_<method> "capture_local"  {index-2}
                            # LOAD_CONST <local name>        {index-1}
                            # CALL_FUNCTION 1                {index+0}
                            helper.deleteRegion(index - 2, index + 1)
                            helper.insertRegion(
                                index,
                                [
                                    dis.Instruction(
                                        "LOAD_FAST",
                                        PyOpcodes.LOAD_FAST,
                                        self.patcher.ensureVarName(local),
                                        local,
                                        local,
                                        0,
                                        0,
                                        False,
                                    )
                                ],
                            )

                            print(
                                f"found local variable read-only access onto '{local}'; replacing with link to real local at index {self.patcher.ensureVarName(local)}"
                            )

                        break
            else:
                break

        print(
            "protected",
            ("'" + "', '".join(captured_names) + "'") if captured_names else "null",
        )

        # Rebind the captured locals
        for index, instr in list(helper.walk()):
            if instr.opcode in dis.haslocal:
                if instr.argval in captured and index not in captured_indices:
                    name, i = captured[instr.argval]
                    helper.instruction_listing[index] = dis.Instruction(
                        instr.opname,
                        instr.opcode,
                        i,
                        name,
                        name,
                        0,
                        0,
                        False,
                    )
                    protect.add(index)
                    print(
                        f"transforming local access at {index}: '{instr.argval}' to '{name}' (old index: {instr.arg}, new: {i}) ({instr})"
                    )

        # Return becomes jump instruction, the function TAIL is currently not known,
        # so we need to trick it a little by setting its value to -1

        index = -1
        while index < len(helper.instruction_listing) - 1:
            index += 1

            for index, instr in list(helper.walk())[index:]:
                if instr.opname == "RETURN_VALUE":
                    helper.deleteRegion(index, index + 1)

                    # If we want to discard the returned result, we need to add a POP_TOP instruction
                    if discard_return_result:
                        helper.insertRegion(
                            index + 2,
                            [
                                dis.Instruction(
                                    "POP_TOP", PyOpcodes.POP_TOP, 0, 0, "", 0, 0, False
                                ),
                                dis.Instruction(
                                    "JUMP_ABSOLUTE",
                                    PyOpcodes.JUMP_ABSOLUTE,
                                    0,
                                    0,
                                    "",
                                    0,
                                    0,
                                    False,
                                ),
                            ],
                        )
                    else:
                        helper.insertRegion(
                            index + 2,
                            [
                                dis.Instruction(
                                    "JUMP_ABSOLUTE",
                                    PyOpcodes.JUMP_ABSOLUTE,
                                    0,
                                    0,
                                    "",
                                    0,
                                    0,
                                    False,
                                ),
                            ],
                        )
                    break
            else:
                break

        # The last return statement does not need a jump_absolute wrapper, as it continues into
        # normal code
        size = len(helper.instruction_listing)
        assert (
            helper.instruction_listing[size - 1].opname == "JUMP_ABSOLUTE"
        ), f"something went horribly wrong, got {helper.instruction_listing[size - 1]}!"
        helper.deleteRegion(size - 1, size)

        index = -1
        while index < len(helper.instruction_listing) - 1:
            index += 1
            for index, instr in list(helper.walk())[index:]:
                if instr.opname == "CALL_FUNCTION" and index > 1:
                    if instr.arg == 1:
                        possible_load = helper.instruction_listing[index - 2]

                        if (
                            possible_load.opname in ("LOAD_GLOBAL", "LOAD_DEREF")
                            and possible_load.argval == "mixin_return"
                        ):
                            # Delete the LOAD_GLOBAL instruction
                            helper.instruction_listing[index] = dis.Instruction(
                                "RETURN_VALUE",
                                PyOpcodes.RETURN_VALUE,
                                None,
                                None,
                                "",
                                0,
                                0,
                                False,
                            )
                            helper.deleteRegion(index - 2, index - 1)
                            index -= 3
                            protect.add(index)
                            break

                    elif instr.arg == 0:
                        possible_load = helper.instruction_listing[index - 1]

                        if (
                            possible_load.opname == "LOAD_GLOBAL"
                            and possible_load.argval == "mixin_return"
                        ):
                            helper.instruction_listing[index - 1] = dis.Instruction(
                                "LOAD_CONST",
                                PyOpcodes.LOAD_CONST,
                                helper.patcher.ensureConstant(None),
                                None,
                                "None",
                                0,
                                0,
                                False,
                            )
                            helper.instruction_listing[index] = dis.Instruction(
                                "RETURN_VALUE",
                                PyOpcodes.RETURN_VALUE,
                                None,
                                None,
                                "",
                                0,
                                0,
                                False,
                            )
                            helper.deleteRegion(index - 2, index - 1)
                            index -= 3
                            protect.add(index - 1)
                            break
            else:
                break

        # Now rebind all
        for index, instr in list(helper.walk()):
            if index in protect:
                continue

            if instr.opcode in dis.hasconst:
                helper.instruction_listing[index] = reconstruct_instruction(
                    instr,
                    self.patcher.ensureConstant(instr.argval),
                )

            elif instr.opcode in dis.haslocal and instr.argval not in captured_names:
                name = instr.argval
                print(f"rebinding real local '{instr.argval}' to '{name}'")
                helper.instruction_listing[index] = reconstruct_instruction(
                    instr,
                    self.patcher.ensureVarName(name),
                    name,
                )

            elif instr.opcode in dis.hasname:
                helper.instruction_listing[index] = reconstruct_instruction(
                    instr,
                    self.patcher.ensureName(instr.argval),
                )

        # And now insert the code into our code
        # todo: check for HEAD generator instruction

        bind_locals = [
            dis.Instruction(
                "STORE_FAST",
                PyOpcodes.STORE_FAST,
                self.patcher.ensureVarName(e),
                e,
                e,
                0,
                0,
                False,
            )
            for e in reversed(method.variable_names[:added_args])
        ]

        self.insertRegion(
            start,
            bind_locals
            + helper.instruction_listing
            + [
                dis.Instruction(
                    "LOAD_CONST",
                    PyOpcodes.LOAD_CONST,
                    self.patcher.ensureConstant("mixin:internal"),
                    None,
                    "",
                    0,
                    0,
                    False,
                ),
                dis.Instruction("POP_TOP", PyOpcodes.POP_TOP, 0, 0, "", 0, 0, False),
            ],
        )
        self.patcher.max_stack_size += target.max_stack_size

        try:
            self.store()
        except:
            self.print_stats()
            raise

        # Find out where the old instruction ended
        for index, instr in self.walk():
            if instr.opname == "LOAD_CONST" and instr.argval == "mixin:internal":
                following = self.instruction_listing[index + 1]
                assert following.opname == "POP_TOP"
                self.deleteRegion(index, index + 2)
                tail_index = index
                break
        else:
            self.print_stats()
            raise RuntimeError("Tail not found after insertion!")

        for index, instr in list(self.walk())[start:tail_index]:
            if instr.opname == "JUMP_ABSOLUTE" and instr.argval == 0:
                self.instruction_listing[index] = reconstruct_instruction(
                    instr,
                    tail_index,
                )

    def insertMethodMultipleTimesAt(
        self,
        start: typing.List[int],
        method: FunctionPatcher,
        force_multiple_inlines=False,
    ):
        """
        Similar to insertMethodAt(), but is able to do some more optimisations in how to inject the method.
        Works best when used with multiple injection targets

        :param start: the start to inject at
        :param method: the method to inject
        :param force_multiple_inlines: if we should force multiple inlines for each method call, or if we can
            optimise stuff

        todo: how can we remember the old instruction offset?
        """
        raise RuntimeError

    def makeMethodAsync(self):
        """
        Simply makes this method async, like it was declared by "async def"
        """
        # don't insert the GEN_START instruction twice
        if self.is_async:
            return

        self.insertRegion(
            -1, [dis.Instruction("GEN_START", 129, 2, None, None, False, 0, 0)]
        )
        self.is_async = True
        return self

    def makeMethodSync(self):
        """
        Simply makes this method sync, like it was declared without "async def"
        """
        if not self.is_async:
            return

        assert self.instruction_listing[0].opname == "GEN_START"

        self.deleteRegion(0, 1)
        self.is_async = False
        return self

    def insertGivenMethodCallAt(
        self,
        offset: int,
        method: typing.Callable,
        *args,
        collected_locals=tuple(),
        pop_result=True,
        include_stack_top_copy=False,
        special_args_collectors: typing.Iterable[dis.Instruction] = tuple(),
        insert_after=tuple(),
    ):
        """
        Injects the given method as a constant call into the bytecode of that function

        :param offset: the offset to inject at
        :param method: the method to inject
        :param collected_locals: what locals to send to the method call
        :param pop_result: if to pop the result
        :param include_stack_top_copy: if to add the stack top as the last parameter
        :param special_args_collectors: args collecting instructions for some stuff,
            the entry count represents the arg count added here
        :param insert_after: an iterable of instructions to insert after the method call
        """
        self.insertRegion(
            offset,
            (
                [
                    dis.Instruction(
                        "DUP_TOP",
                        PyOpcodes.DUP_TOP,
                        0,
                        None,
                        "",
                        False,
                        0,
                        False,
                    ),
                ]
                if include_stack_top_copy
                else []
            )
            + [
                dis.Instruction(
                    "LOAD_CONST",
                    PyOpcodes.LOAD_CONST,
                    self.patcher.ensureConstant(method),
                    method,
                    repr(method),
                    False,
                    0,
                    False,
                ),
            ]
            + (
                [
                    dis.Instruction(
                        "ROT_TWO",
                        PyOpcodes.ROT_TWO,
                        0,
                        None,
                        "",
                        False,
                        0,
                        False,
                    )
                ]
                if include_stack_top_copy
                else []
            )
            + [
                dis.Instruction(
                    "LOAD_CONST",
                    PyOpcodes.LOAD_CONST,
                    self.patcher.ensureConstant(e),
                    e,
                    repr(e),
                    False,
                    0,
                    0,
                )
                for e in reversed(args)
            ]
            + [
                dis.Instruction(
                    "LOAD_FAST",
                    PyOpcodes.LOAD_FAST,
                    self.patcher.ensureVarName(e),
                    e,
                    e,
                    False,
                    0,
                    0,
                )
                for e in reversed(collected_locals)
            ]
            + list(special_args_collectors)
            + [
                dis.Instruction(
                    "CALL_FUNCTION",
                    PyOpcodes.CALL_FUNCTION,
                    len(args)
                    + len(collected_locals)
                    + int(include_stack_top_copy)
                    + len(special_args_collectors),
                    None,
                    None,
                    False,
                    0,
                    0,
                ),
            ]
            + (
                [
                    dis.Instruction(
                        "POP_TOP", PyOpcodes.POP_TOP, 0, None, None, False, 0, 0
                    ),
                ]
                if pop_result
                else []
            )
            + list(insert_after),
        )
        self.patcher.max_stack_size += (
            1
            + len(args)
            + len(collected_locals)
            + int(include_stack_top_copy)
            + len(special_args_collectors)
        )
        return self

    def insertStaticMethodCallAt(self, offset: int, method: str, *args):
        """
        Injects a static method call into another method
        :param offset: the offset to inject at, from function head
        :param method: the method address to inject, by module:path
        :param args: the args to invoke with

        WARNING: due to the need of a dynamic import instruction, the method to inject into cannot lie in the same
            package as the method call to inject
        todo: add option to load the method beforehand and inject as constant
        """

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
                self.patcher.ensureName(real_module),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "IMPORT_FROM",
                109,
                self.patcher.ensureName(real_name),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "STORE_FAST",
                125,
                self.patcher.ensureName(real_module),
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
                self.patcher.ensureName(real_module),
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
        return self

    def insertAsyncStaticMethodCallAt(self, offset: int, method: str, *args):
        """
        Injects a static method call to an async method into another method
        :param offset: the offset to inject at, from function head
        :param method: the method address to inject, by module:path
        :param args: the args to invoke with

        WARNING: due to the need of a dynamic import instruction, the method to inject into cannot lie in the same
            package as the method call to inject
        todo: add option to load the method beforehand and inject as constant
        """

        if not self.is_async:
            raise RuntimeError(
                "cannot insert async method call when surrounding method is not async"
            )

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
                self.patcher.ensureName(real_module),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "IMPORT_FROM",
                109,
                self.patcher.ensureName(real_name),
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "STORE_FAST",
                125,
                self.patcher.ensureName(real_module),
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
                self.patcher.ensureName(real_module),
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
                "GET_AWAITABLE",
                73,
                0,
                None,
                None,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "LOAD_CONST",
                100,
                self.patcher.ensureConstant(None),
                0,
                0,
                False,
                0,
                0,
            ),
            dis.Instruction(
                "YIELD_FROM",
                72,
                0,
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
        return self

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

    def print_stats(self):
        try:
            self.store()
        except:
            traceback.print_exc()
            for i, instr in enumerate(self.instruction_listing):
                print(i * 2, instr)
            return

        print(f"MixinMethodWrapper stats around {self.patcher.target}")

        for i, instr in self.walk():
            print(i * 2, instr)

        print("Raw code:", self.patcher.code_string)
        print("Names:", self.patcher.names)
        print("Constants:", self.patcher.constants)
        print("Free vars:", self.patcher.free_vars)
        print("Cell vars:", self.patcher.cell_vars)

    def findSourceOfStackIndex(
        self, index: int, offset: int
    ) -> typing.Iterator[dis.Instruction]:
        """
        Finds the source instruction of the given stack element.
        Uses advanced back-tracking in code

        :param index: current instruction index, before which we want to know the layout
        :param offset: the offset, where 0 is top, and all following numbers (1, 2, 3, ...) give the i+1-th
            element of the stack
        """

        for instr in reversed(self.instruction_listing[:index]):
            if offset < 0:
                raise RuntimeError

            if offset == 0:  # Currently, at top
                if instr.opcode in LOAD_SINGLE_VALUE:
                    yield instr
                    return

                elif (
                    instr.opcode in POP_DOUBLE_AND_PUSH_SINGLE
                    or instr.opcode in POP_SINGLE_AND_PUSH_SINGLE
                ):
                    yield instr
                    return

            if instr.opcode in POP_SINGLE_AND_PUSH_SINGLE:
                continue

            if instr.opcode in LOAD_SINGLE_VALUE:
                offset -= 1

            elif instr.opcode in POP_SINGLE_VALUE:
                offset += 1

            elif instr.opcode in POP_DOUBLE_AND_PUSH_SINGLE:
                offset += 1

            elif instr.opcode in POP_DOUBLE_VALUE:
                offset += 2

            elif instr.opcode == PyOpcodes.CALL_METHOD:
                offset += 1
                offset -= instr.arg

            elif instr.opcode == PyOpcodes.UNPACK_SEQUENCE:
                offset += instr.arg - 1

            elif instr.opcode == PyOpcodes.FOR_ITER:
                raise ValueError

            else:
                raise NotImplementedError(instr)

        if offset < 0:
            raise RuntimeError
