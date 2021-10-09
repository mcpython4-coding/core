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

from ..engine import logger
from .MixinMethodWrapper import capture_local, mixin_return


class AbstractMixinProcessor:
    """
    Mixin processor class
    Stuff that works on methods on a high level
    """

    def canBeAppliedOnModified(
        self,
        handler: "MixinHandler",
        function: types.FunctionType,
        modifier_list: typing.List["AbstractMixinProcessor"],
    ) -> bool:
        return True

    def canBeFurtherModified(
        self, handler: "MixinHandler", function: types.FunctionType
    ) -> bool:
        return True

    def apply(
        self,
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
    ):
        pass


class MixinReplacementProcessor(AbstractMixinProcessor):
    def __init__(self, replacement: types.FunctionType):
        self.replacement = replacement

    def canBeFurtherModified(
        self, handler: "MixinHandler", function: types.FunctionType
    ) -> bool:
        return False

    def apply(
        self,
        handler: "MixinHandler",
        target: mcpython.mixin.PyBytecodeManipulator.FunctionPatcher,
    ):
        target.overrideFrom(
            mcpython.mixin.PyBytecodeManipulator.FunctionPatcher(self.replacement)
        )


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

    def __init__(self, processor_name: str, skip_on_fail=False, priority=0):
        self.processor_name = processor_name
        self.skip_on_fail = skip_on_fail
        self.priority = priority
        self.bound_mixin_processors: typing.Dict[
            str, typing.List[AbstractMixinProcessor]
        ] = {}

    def applyMixins(self):
        for target, mixins in self.bound_mixin_processors.items():
            logger.println(
                f"[MIXIN][WARN] applying mixins of '{self.processor_name}' onto '{target}'"
            )

            patcher = mcpython.mixin.PyBytecodeManipulator.FunctionPatcher(
                self.lookup_method(target)
            )

            for mixin in mixins:
                logger.println("[MIXIN][WARN] applying mixin " + str(mixin))

                mixin.apply(self, patcher)

            patcher.applyPatches()

    @staticmethod
    def lookup_method(method: str):
        module, path = method.split(":")
        module = importlib.import_module(module)

        for e in path.split("."):
            module = getattr(module, e)

        return module

    def replace_function_body(
        self, access_str: str
    ) -> typing.Callable[[types.FunctionType], types.FunctionType]:
        def annotate(function):
            self.bound_mixin_processors.setdefault(access_str, []).append(
                MixinReplacementProcessor(function)
            )
            return function

        return annotate

    def inline_method_calls(self, access_str: str, method_call_target: str):
        """
        Inlines all method calls to a defined function
        Does not work like the normal inline-keyword, as we cannot find all method calls

        WARNING: method must be looked up for it to work
        WARNING: when someone mixes into the method to inline AFTER this mixin applies,
            the change will not be affecting this method

        This is not a real mixin, but a self-modifier
        """
        return lambda e: e

    def inject_at_head(self, access_str: str):
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
    ):
        """
        Injects code at specific return statements
        :param access: the method
        :param return_sampler: a method checking a return statement, signature not defined by now
        :param include_previous_mixed_ins: if return statements from other mixins should be included in the search
        """
        return lambda e: e

    def inject_replace_method_invoke(
        self, access: str, target_method: str, sampler=lambda *_: True, inline=True
    ):
        """
        Modifies method calls to call another method
        :param access: the method
        :param target_method: the method to replace
        :param sampler: optionally, some checker for invoke call
        :param inline: when True, will inline this annotated method into the target
        """
        return lambda e: e
