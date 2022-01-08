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

from mcpython.mixin.InstructionMatchers import AbstractInstructionMatcher
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
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
    def __init__(self, target_func: typing.Callable, *args):
        self.target_func = target_func
        self.args = args

    def apply(
        self,
        handler,
        target: FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        index = 0 if helper.instruction_listing[0].opname != "GEN_START" else 1
        helper.insertGivenMethodCallAt(index, self.target_func, *self.args)
        helper.store()


class InjectFunctionCallAtReturnProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher

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

                helper.insertGivenMethodCallAt(index - 1, self.target_func, *self.args)

        helper.store()


class InjectFunctionCallAtYieldProcessor(AbstractMixinProcessor):
    def __init__(
        self,
        target_func: typing.Callable,
        *args,
        matcher: AbstractInstructionMatcher = None,
    ):
        self.target_func = target_func
        self.args = args
        self.matcher = matcher

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

                helper.insertGivenMethodCallAt(
                    index - 4,
                    self.target_func,
                    *(instr.opname == "YIELD_FROM",) + self.args,
                )

        helper.store()
