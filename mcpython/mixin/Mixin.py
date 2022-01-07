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
import importlib
import types
import typing

import mcpython.mixin.PyBytecodeManipulator
from .MixinMethodWrapper import MixinPatchHelper

from ..engine import logger
from .MixinMethodWrapper import mixin_return


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
    def __init__(self, before, after, fail_on_not_found=False):
        self.before = before
        self.after = after
        self.fail_on_not_found = fail_on_not_found

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

        helper.replaceConstant(self.before, self.after)
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

    def replace_method_constant(self, access_str: str, constant_value, new_value, priority=0, optional=True, fail_on_not_found=True):
        """
        Replaces a given constant globally in the method
        :param access_str: the access_str for the target
        :param constant_value: the original value
        :param new_value: the new value
        :param priority: the mixin priority
        :param optional: optional mixin?
        :param fail_on_not_found: if mixin applying failed if the constant was not found
        """
        self.bound_mixin_processors.setdefault(access_str, []).append((
            MixinConstantReplacer(constant_value, new_value, fail_on_not_found=fail_on_not_found), priority, optional
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
