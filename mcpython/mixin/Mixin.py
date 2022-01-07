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
import importlib
import types
import typing

import mcpython.mixin.PyBytecodeManipulator
from .MixinMethodWrapper import MixinPatchHelper
from .util import PyOpcodes

from ..engine import logger
from .MixinMethodWrapper import mixin_return


class AbstractInstructionMatcher:
    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        raise NotImplementedError

    def __and__(self, other):
        if isinstance(other, AndMatcher):
            return AndMatcher(self, *other.matchers)

        return AndMatcher(self, other)

    def __or__(self, other):
        if isinstance(other, OrMatcher):
            return OrMatcher(self, *other.matchers)

        return OrMatcher(self, other)

    def __invert__(self):
        return NotMatcher(self)


class AndMatcher(AbstractInstructionMatcher):
    def __init__(self, *matchers: AbstractInstructionMatcher):
        self.matchers = matchers

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        return all(matcher.matches(function, index, match_count) for matcher in self.matchers)

    def __and__(self, other):
        if isinstance(other, AndMatcher):
            return AndMatcher(*self.matchers, *other.matchers)
        return AndMatcher(*self.matchers, other)


class OrMatcher(AbstractInstructionMatcher):
    def __init__(self, *matchers: AbstractInstructionMatcher):
        self.matchers = matchers

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        return any(matcher.matches(function, index, match_count) for matcher in self.matchers)

    def __or__(self, other):
        if isinstance(other, OrMatcher):
            return OrMatcher(*self.matchers, *other.matchers)
        return OrMatcher(*self.matchers, other)


class NotMatcher(AbstractInstructionMatcher):
    def __init__(self, matcher: AbstractInstructionMatcher):
        self.matcher = matcher

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        return not self.matcher.matches(function, index, match_count)


class AnyByInstructionNameMatcher(AbstractInstructionMatcher):
    def __init__(self, opname: str):
        self.opname = opname

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        return function.instruction_listing[index].opname == self.opname


class IndexBasedMatcher(AbstractInstructionMatcher):
    def __init__(self, start: int, end: int = None, sub_matcher: AbstractInstructionMatcher = None):
        self.start = start
        self.end = end
        self.sub_matcher = sub_matcher

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        if index < self.start: return False
        if self.end is not None and index > self.end: return False
        if self.sub_matcher:
            return self.sub_matcher.matches(function, index, match_count)

        return True


class SurroundingBasedMatcher(AbstractInstructionMatcher):
    def __init__(self, this_matcher: AbstractInstructionMatcher = None):
        self.this_matcher = this_matcher
        self.size = 0, 0
        self.matchers: typing.Tuple[typing.List[AbstractInstructionMatcher], typing.List[AbstractInstructionMatcher]] = [], []

    def set_offset_matcher(self, offset: int, matcher: AbstractInstructionMatcher):
        if offset < 0:
            self.size = min(offset, self.size[0]), self.size[1]
            if len(self.matchers[0]) < abs(offset):
                self.matchers[0] += [None] * (abs(offset) - len(self.matchers[0]))
            self.matchers[0][offset] = matcher
        else:
            self.size = self.size[0], max(offset, self.size[1])
            if len(self.matchers[1]) < offset:
                self.matchers[0] += [None] * (offset - len(self.matchers[0]))
            self.matchers[1][offset-1] = matcher

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        if index + self.size[0] < 0 or index + self.size[1] >= len(function.patcher.code.co_code) // 2:
            return False

        for i in range(len(self.matchers[0])):
            dx = -(len(self.matchers[0]) - i)
            if not self.matchers[0][i].matches(function, index+dx, match_count):
                return False

        for i in range(len(self.matchers[1])):
            if not self.matchers[0][i].matches(function, index+i+1, match_count):
                return False

        if self.this_matcher is not None:
            return self.this_matcher.matches(function, index, match_count)

        return True


class LoadConstantValueMatcher(AbstractInstructionMatcher):
    def __init__(self, value):
        self.value = value

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        instr = function.instruction_listing[index]
        return instr.opname == "LOAD_CONST" and instr.argval == self.value


class LoadGlobalMatcher(AbstractInstructionMatcher):
    def __init__(self, global_name: str):
        self.global_name = global_name

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        instr = function.instruction_listing[index]
        return instr.opname == "LOAD_GLOBAL" and instr.argval == self.global_name


class CounterMatcher(AbstractInstructionMatcher):
    def __init__(self, count_start: int, count_end: int = None):
        self.count_start = count_start
        self.count_end = count_end or count_start

    def matches(self, function: MixinPatchHelper, index: int, match_count: int) -> bool:
        return self.count_start <= match_count <= self.count_end


# todo: implement more matchers

class AbstractMixinProcessor:
    """
    Mixin processor class
    Stuff that works on methods on a high level
    """

    def canBeAppliedOnModified(
        self,
        handler: "MixinHandler",
        function: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
        modifier_list: typing.List["AbstractMixinProcessor"],
    ) -> bool:
        return True

    def apply(
        self,
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
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
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        target.overrideFrom(
            mcpython.mixin.PyBytecodeManipulator.FunctionPatcher(self.replacement)
        )

    def is_breaking(self) -> bool:
        return True


class MixinConstantReplacer(AbstractMixinProcessor):
    def __init__(self, before, after, fail_on_not_found=False, matcher: AbstractInstructionMatcher = None):
        self.before = before
        self.after = after
        self.fail_on_not_found = fail_on_not_found
        self.matcher = matcher

    def apply(
        self,
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        if self.before not in target.constants:
            if self.fail_on_not_found:
                raise RuntimeError(f"constant {self.before} not found in target {target} (to be replaced with {self.after})")
            return

        helper.replaceConstant(self.before, self.after, matcher=self.matcher.matches if self.matcher is not None else None)
        helper.store()


class MixinGlobal2ConstReplace(AbstractMixinProcessor):
    def __init__(self, global_name: str, after, matcher: AbstractInstructionMatcher = None):
        self.global_name = global_name
        self.after = after
        self.matcher = matcher

    def apply(
        self,
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
        helper: MixinPatchHelper,
    ):
        match = -1
        for index, instruction in helper.getLoadGlobalsLoading(self.global_name):
            match += 1

            if self.matcher is not None and not self.matcher.matches(helper, index, match):
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


class MixinHandler:
    """
    Handler for mixing into some functions

    Create one of this object per mixin group

    This is than an annotation holder, working the following way:

    @<instance>.<some modifier>(<target address>, <...args>)
    def <some override>(...):
        ...

    Please make sure that the signatures match up, when not other specified

    By default, control flow with "return"'s is only arrival in the specified section.
    Use mixin_return() followed by a normal return to exit the method injected into
    """
    LOCKED = False

    def __init__(self, processor_name: str, skip_on_fail=False, priority=0):
        if MixinHandler.LOCKED:
            raise RuntimeError()

        self.processor_name = processor_name
        self.skip_on_fail = skip_on_fail
        self.priority = priority
        self.bound_mixin_processors: typing.Dict[
            str, typing.List[typing.Tuple[AbstractMixinProcessor, float, bool]]
        ] = {}

    def applyMixins(self):
        for target, mixins in self.bound_mixin_processors.items():
            logger.println(
                f"[MIXIN][WARN] applying mixins of '{self.processor_name}' onto '{target}'"
            )

            method_target = self.lookup_method(target)
            patcher = mcpython.mixin.PyBytecodeManipulator.FunctionPatcher(
                method_target
            )
            helper = MixinPatchHelper(patcher)

            order = sorted(sorted(mixins, key=lambda e: 0 if e[2] else 1), key=lambda e: e[1])

            non_optionals = set()
            optionals = set()
            to_delete = []
            for i, (mixin, priority, optional) in enumerate(order):
                if non_optionals and mixin.is_breaking():
                    logger.println("[MIXIN][FATAL] conflicting mixin: found an non-optional mixin before, breaking with this mixin!")
                    raise RuntimeError

                elif optionals and mixin.is_breaking():
                    to_delete += [e[1] for e in optionals]
                    optionals.clear()

                previous = [e[0] for x, e in enumerate(order[:i]) if x not in to_delete]
                if previous and not mixin.canBeAppliedOnModified(self, patcher, previous):
                    if optional:
                        to_delete.append(i)
                    else:
                        if non_optionals and mixin.is_breaking():
                            logger.println("[MIXIN][FATAL] conflicting mixin: found an non-optional mixin before, breaking with this mixin!")
                            raise RuntimeError

                if not optional:
                    non_optionals.add(mixin)
                else:
                    optionals.add((mixin, i))

            for i in sorted(to_delete, reverse=True):
                mixin, priority, optional = order[i]
                logger.println(f"[MIXIN][WARN] skipping mixin {mixin} with priority {priority} (optional: {optional})")
                del order[i]

            for mixin, priority, optional in order:
                logger.println(f"[MIXIN][WARN] applying mixin {mixin} with priority {priority} (optional: {optional})")
                mixin.apply(self, patcher, helper)

            patcher.applyPatches()

    @staticmethod
    def lookup_method(method: str):
        module, path = method.split(":")
        module = importlib.import_module(module)

        for e in path.split("."):
            module = getattr(module, e)

        return module

    def replace_method_constant(self, access_str: str, constant_value, new_value, priority=0, optional=True, fail_on_not_found=True, matcher: AbstractInstructionMatcher = None):
        """
        Replaces a given constant globally in the method
        :param access_str: the access_str for the target
        :param constant_value: the original value
        :param new_value: the new value
        :param priority: the mixin priority
        :param optional: optional mixin?
        :param fail_on_not_found: if mixin applying failed if the constant was not found
        :param matcher: a custom instruction matcher, optional, when None, matches all instructions using that constant
        """
        self.bound_mixin_processors.setdefault(access_str, []).append((
            MixinConstantReplacer(constant_value, new_value, fail_on_not_found=fail_on_not_found, matcher=matcher), priority, optional
        ))
        return self

    def replace_global_with_constant(self, access_str: str, global_name: str, new_value, priority=0, optional=True, matcher: AbstractInstructionMatcher = None):
        """
        Replaces all LOAD_GLOBAL <global name> instructions with a LOAD_CONST(new value) instructions
        :param access_str: the access str of the method
        :param global_name: the global name
        :param new_value: the new value
        :param priority: the mixin priority
        :param optional: optional mixin?
        :param matcher: the instruction matcher object
        """
        self.bound_mixin_processors.setdefault(access_str, []).append((
            MixinGlobal2ConstReplace(global_name, new_value, matcher=matcher), priority, optional
        ))
        return self

    def replace_function_body(
        self, access_str: str, priority=0, optional=True
    ) -> typing.Callable[[types.FunctionType], types.FunctionType]:
        def annotate(function):
            self.bound_mixin_processors.setdefault(access_str, []).append(
                (MixinReplacementProcessor(function), priority, optional)
            )
            return function

        return annotate

    def inline_method_calls(self, access_str: str, method_call_target: str, priority=0, optional=True):
        """
        Inlines all method calls to a defined function
        Does not work like the normal inline-keyword, as we cannot find all method calls

        WARNING: method must be looked up for it to work
        WARNING: when someone mixes into the method to inline AFTER this mixin applies,
            the change will not be affecting this method

        This is not a real mixin, but a self-modifier
        """
        return lambda e: e

    def inject_at_head(self, access_str: str, priority=0, optional=True):
        """
        Injects some code at the function head
        Can be used for e.g. parameter manipulation
        """
        return lambda e: e

    def inject_at_return(
        self,
        access: str,
        return_sampler=lambda *_: True,
        include_previous_mixed_ins=False,
        priority=0,
        optional=True
    ):
        """
        Injects code at specific return statements
        :param access: the method
        :param return_sampler: a method checking a return statement, signature not defined by now
        :param include_previous_mixed_ins: if return statements from other mixins should be included in the search
        :param priority: the mixin priority
        :param optional: optional mixin?
        """
        return lambda e: e

    def inject_replace_method_invoke(
        self, access: str, target_method: str, sampler=lambda *_: True, inline=True, priority=0, optional=True
    ):
        """
        Modifies method calls to call another method
        :param access: the method
        :param target_method: the method to replace
        :param sampler: optionally, some checker for invoke call
        :param inline: when True, will inline this annotated method into the target
        :param priority: the mixin priority
        :param optional: optional mixin?
        """
        return lambda e: e


mixin_handler = MixinHandler("global")
MixinHandler.LOCKED = True
