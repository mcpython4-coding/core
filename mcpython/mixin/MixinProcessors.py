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
import types
import typing

from mcpython.engine import logger
from mcpython.mixin.InstructionMatchers import AbstractInstructionMatcher
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper, reconstruct_instruction
from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher
from mcpython.mixin.util import PyOpcodes


class AbstractMixinProcessor:
    """
    Mixin processor class
    Stuff that works on methods on a high level
    """

    def canBeAppliedOnModified(
        self,
        handler,
        function: FunctionPatcher,
        modifier_list: typing.List["AbstractMixinProcessor"],
    ) -> bool:
        return True

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        """
        Applies the mixin processor to the target
        :param handler: the handler instance
        :param target: the target FunctionPatcher instance
        :param helper: the helper instance, the method is responsible for invoking store() on it
        """
        pass

    def is_breaking(self) -> bool:
        return False


class MixinReplacementProcessor(AbstractMixinProcessor):
    def __init__(self, replacement: types.FunctionType):
        self.replacement = replacement

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        target.overrideFrom(FunctionPatcher(self.replacement))

    def is_breaking(self) -> bool:
        return True


class MixinConstantReplacer(AbstractMixinProcessor):
    def __init__(
        self,
        before,
        after,
        fail_on_not_found=False,
        matcher: AbstractInstructionMatcher = None,
    ):
        self.before = before
        self.after = after
        self.fail_on_not_found = fail_on_not_found
        self.matcher = matcher

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        if self.before not in target.constants:
            if self.fail_on_not_found:
                raise RuntimeError(
                    f"constant {self.before} not found in target {target} (to be replaced with {self.after})"
                )
            return

        helper.replaceConstant(
            self.before,
            self.after,
            matcher=self.matcher.matches if self.matcher is not None else None,
        )
        helper.store()


class MixinGlobal2ConstReplace(AbstractMixinProcessor):
    def __init__(
        self, global_name: str, after, matcher: AbstractInstructionMatcher = None
    ):
        self.global_name = global_name
        self.after = after
        self.matcher = matcher

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        match = -1
        for index, instruction in helper.getLoadGlobalsLoading(self.global_name):
            match += 1

            if self.matcher is not None and not self.matcher.matches(
                helper, index, match
            ):
                continue

            helper.instruction_listing[index] = dis.Instruction(
                "LOAD_CONST",
                PyOpcodes.LOAD_CONST,
                target.ensureConstant(self.after),
                self.after,
                repr(self.after),
                instruction.offset,
                instruction.starts_line,
                instruction.is_jump_target,
            )

        helper.store()


class MixinLocal2ConstReplace(AbstractMixinProcessor):
    def __init__(
        self, local_name: str, after, matcher: AbstractInstructionMatcher = None
    ):
        self.local_name = local_name
        self.after = after
        self.matcher = matcher

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        match = -1
        for index, instruction in enumerate(helper.instruction_listing):
            if instruction.opname != "LOAD_FAST":
                continue
            if helper.patcher.variable_names[instruction.arg] != self.local_name:
                continue

            match += 1

            if self.matcher is not None and not self.matcher.matches(
                helper, index, match
            ):
                continue

            helper.instruction_listing[index] = dis.Instruction(
                "LOAD_CONST",
                PyOpcodes.LOAD_CONST,
                target.ensureConstant(self.after),
                self.after,
                repr(self.after),
                instruction.offset,
                instruction.starts_line,
                instruction.is_jump_target,
            )

        helper.store()


class MixinGlobalReTargetProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        previous_global: str,
        new_global: str,
        matcher: AbstractInstructionMatcher = None,
    ):
        self.previous_global = previous_global
        self.new_global = new_global
        self.matcher = matcher

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        match = -1
        for index, instruction in helper.getLoadGlobalsLoading(self.previous_global):
            match += 1

            if self.matcher is not None and not self.matcher.matches(
                helper, index, match
            ):
                continue

            helper.instruction_listing[index] = dis.Instruction(
                "LOAD_GLOBAL",
                PyOpcodes.LOAD_GLOBAL,
                target.ensureName(self.new_global),
                self.new_global,
                None,
                instruction.offset,
                instruction.starts_line,
                instruction.is_jump_target,
            )

        helper.store()


class InjectFunctionCallAtHeadProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        collected_locals=tuple(),
        inline=False,
    ):
        self.target_func = target_func
        self.args = args
        self.collected_locals = collected_locals
        self.inline = inline

        if inline:
            assert (
                len(collected_locals) == 0
            ), "cannot inline when collecting local variables"

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        index = 0 if helper.instruction_listing[0].opname != "GEN_START" else 1

        if not self.inline:
            helper.insertGivenMethodCallAt(
                index,
                self.target_func,
                *self.args,
                collected_locals=self.collected_locals,
            )
        else:
            # todo: can we inline somehow the arg values?
            helper.insertMethodAt(
                index,
                self.target_func,
            )

        helper.store()


class InjectFunctionCallAtReturnProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
        collected_locals=tuple(),
        add_return_value=False,
        inline=False,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher
        self.collected_locals = collected_locals
        self.add_return_value = add_return_value
        self.inline = inline

        if inline:
            assert (
                len(collected_locals) == 0
            ), "cannot inline when collecting local variables"

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        matches = -1
        for index, instr in enumerate(helper.instruction_listing):
            if instr.opname == "RETURN_VALUE":
                matches += 1

                if self.matcher is not None and not self.matcher.matches(
                    helper, index, matches
                ):
                    continue

                if not self.inline:
                    helper.insertGivenMethodCallAt(
                        index - 1 if not self.add_return_value else index,
                        self.target_func,
                        *self.args,
                        collected_locals=self.collected_locals,
                        include_stack_top_copy=self.add_return_value,
                    )
                else:
                    helper.insertMethodAt(
                        index - 1 if not self.add_return_value else index,
                        self.target_func,
                    )

        helper.store()


class InjectFunctionCallAtReturnReplaceValueProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
        collected_locals=tuple(),
        add_return_value=False,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher
        self.collected_locals = collected_locals
        self.add_return_value = add_return_value

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        matches = -1
        for index, instr in enumerate(helper.instruction_listing):
            if instr.opname == "RETURN_VALUE":
                matches += 1

                if self.matcher is not None and not self.matcher.matches(
                    helper, index, matches
                ):
                    continue

                helper.insertRegion(
                    index,
                    [
                        dis.Instruction(
                            "POP_TOP", PyOpcodes.POP_TOP, 0, None, None, False, 0, 0
                        )
                    ],
                )
                helper.insertGivenMethodCallAt(
                    index + 1,
                    self.target_func,
                    *self.args,
                    collected_locals=self.collected_locals,
                    pop_result=False,
                    include_stack_top_copy=self.add_return_value,
                )

        helper.store()


class InjectFunctionCallAtYieldProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
        collected_locals=tuple(),
        add_yield_value=False,
        inline=False,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher
        self.collected_locals = collected_locals
        self.add_yield_value = add_yield_value
        self.inline = inline

        if inline:
            assert (
                len(collected_locals) == 0
            ), "cannot inline when collecting local variables"

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        matches = -1
        for index, instr in enumerate(helper.instruction_listing):
            if instr.opname == "YIELD_VALUE" or instr.opname == "YIELD_FROM":
                matches += 1

                if self.matcher is not None and not self.matcher.matches(
                    helper, index, matches
                ):
                    continue

                if not self.inline:
                    helper.insertGivenMethodCallAt(
                        index,
                        self.target_func,
                        *(instr.opname == "YIELD_FROM",) + self.args,
                        collected_locals=self.collected_locals,
                        include_stack_top_copy=self.add_yield_value,
                    )
                else:
                    helper.insertMethodAt(
                        index,
                        self.target_func,
                    )

        helper.store()


class InjectFunctionCallAtYieldReplaceValueProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
        collected_locals=tuple(),
        add_yield_value=False,
        is_yield_from=False,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher
        self.collected_locals = collected_locals
        self.add_yield_value = add_yield_value
        self.is_yield_from = is_yield_from

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        matches = -1
        for index, instr in enumerate(helper.instruction_listing):
            if instr.opname == "YIELD_VALUE" or instr.opname == "YIELD_FROM":
                matches += 1

                # Do we need to change the instruction type?
                if self.is_yield_from is not None and (
                    self.is_yield_from != instr.opname == "YIELD_FROM"
                ):
                    if self.is_yield_from:
                        helper.instruction_listing[index] = dis.Instruction(
                            "YIELD_FROM",
                            PyOpcodes.YIELD_FROM,
                            0,
                            None,
                            "",
                            0,
                            0,
                            False,
                        )
                    else:
                        helper.instruction_listing[index] = dis.Instruction(
                            "YIELD_VALUE",
                            PyOpcodes.YIELD_VALUE,
                            0,
                            None,
                            "",
                            0,
                            0,
                            False,
                        )

                if self.matcher is not None and not self.matcher.matches(
                    helper, index, matches
                ):
                    continue

                helper.insertRegion(
                    index,
                    [
                        dis.Instruction(
                            "POP_TOP", PyOpcodes.POP_TOP, 0, None, None, False, 0, 0
                        )
                    ],
                )

                helper.insertGivenMethodCallAt(
                    index + (0 if self.add_yield_value else 1),
                    self.target_func,
                    *(instr.opname == "YIELD_FROM",) + self.args,
                    collected_locals=self.collected_locals,
                    pop_result=False,
                    include_stack_top_copy=self.add_yield_value,
                )

        helper.store()


class InjectFunctionCallAtTailProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        collected_locals=tuple(),
        add_return_value=False,
        inline=False,
    ):
        self.target_func = target_func
        self.args = args
        self.collected_locals = collected_locals
        self.add_return_value = add_return_value
        self.inline = inline

        if inline:
            assert (
                len(collected_locals) == 0
            ), "cannot inline when collecting local variables"

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        assert (
            helper.instruction_listing[-1].opname == "RETURN_VALUE"
        ), "integrity of function failed!"

        if not self.inline:
            helper.insertGivenMethodCallAt(
                len(helper.instruction_listing) - 1,
                self.target_func,
                *self.args,
                collected_locals=self.collected_locals,
                include_stack_top_copy=self.add_return_value,
            )
        else:
            helper.insertMethodAt(
                len(helper.instruction_listing) - 1,
                self.target_func,
            )

        helper.store()


class InjectFunctionLocalVariableModifier(AbstractMixinProcessor):
    def __init__(
        self,
        function: typing.Callable,
        local_variables: typing.List[str],
        matcher: AbstractInstructionMatcher,
        *args,
        collected_locals=tuple(),
    ):
        self.function = function
        self.local_variables = local_variables
        self.args = args
        self.matcher = matcher
        self.collected_locals = collected_locals

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        collected_locals = [
            dis.Instruction(
                "LOAD_FAST",
                PyOpcodes.LOAD_FAST,
                helper.patcher.ensureVarName(e),
                e,
                e,
                0,
                0,
                False,
            )
            for e in reversed(self.local_variables)
        ]
        store_locals = [
            dis.Instruction(
                "UNPACK_SEQUENCE",
                PyOpcodes.UNPACK_SEQUENCE,
                len(self.local_variables),
                0,
                "",
                0,
                0,
                False,
            )
        ] + [
            dis.Instruction(
                "STORE_FAST",
                PyOpcodes.STORE_FAST,
                helper.patcher.ensureVarName(e),
                e,
                e,
                0,
                0,
                False,
            )
            for e in reversed(self.local_variables)
        ]

        for index, instruction in enumerate(helper.instruction_listing):
            if self.matcher.matches(helper, index, index):
                helper.insertGivenMethodCallAt(
                    index,
                    self.function,
                    *self.args,
                    collected_locals=self.collected_locals,
                    special_args_collectors=collected_locals,
                    pop_result=False,
                    insert_after=store_locals,
                )
        helper.store()


class MethodInlineProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        func_name: str,
        target_accessor: typing.Callable[[], typing.Callable] = None,
    ):
        self.func_name = func_name
        self.target_accessor = target_accessor

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        for index, instr in helper.walk():
            if instr.opname == "CALL_METHOD":
                try:
                    source = next(helper.findSourceOfStackIndex(index, instr.arg))

                    print(source, self.func_name)

                    if source.opcode == PyOpcodes.LOAD_METHOD:
                        if (
                            self.func_name.startswith("%.")
                            and source.argval == self.func_name.split(".")[-1]
                        ):
                            if self.target_accessor is not None:
                                helper.deleteInstruction(instr)
                                helper.insertMethodAt(
                                    index,
                                    self.target_accessor(),
                                    added_args=instr.arg,
                                    discard_return_result=False,
                                )

                    print("source: ", source)
                except ValueError:
                    pass
                except:
                    logger.print_exception(f"during tracing source of {instr}")
