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
import typing

from mcpython.engine import logger
from mcpython.mixin import CodeOptimiser
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
from mcpython.mixin.MixinProcessors import AbstractMixinProcessor, MethodInlineProcessor


class _OptimiserContainer:
    def __init__(self, target):
        self.target = target
        self.is_constant = False
        self.constant_args: typing.Set[str] = set()
        self.code_walkers: typing.List[AbstractMixinProcessor] = []

    def optimise_target(self):
        if isinstance(self.target, typing.Callable):
            helper = MixinPatchHelper(self.target)

            for processor in self.code_walkers:
                logger.println(
                    f"[INFO] applying optimiser mixin {processor} onto {self.target}"
                )
                processor.apply(None, helper.patcher, helper)
                helper.re_eval_instructions()

            helper.store()

            CodeOptimiser.optimise_code(helper)

    async def optimize_target_async(self):
        self.optimise_target()


def _schedule_optimisation(
    target: typing.Callable | typing.Type,
) -> _OptimiserContainer:
    if not hasattr(target, "optimiser_container"):
        target.optimiser_container = _OptimiserContainer(target)

        from mcpython import shared

        if not shared.IS_TEST_ENV:
            shared.mod_loader("minecraft", "stage:mixin:optimise_code")(
                target.optimiser_container.optimize_target_async()
            )

    return target.optimiser_container


def constant_arg(name: str):
    """
    Promises that the given arg will not be modified
    Only affects mutable data types
    Removes the need to copy the data during inlining
    """

    def annotation(target: typing.Callable):
        optimiser = _schedule_optimisation(target)
        optimiser.constant_args.add(name)
        return target

    return annotation


def constant_operation():
    """
    Promises that the method will not affect the state of the system, meaning it is e.g.
    a getter method
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target).is_constant = True
        return target

    return annotation


def mutable_attribute(name: str):
    """
    Marks a certain attribute to be mutable
    Only affects when all_immutable_attributes() is used also on the class
    """

    def annotation(target: typing.Type):
        _schedule_optimisation(target)
        return target

    return annotation


def immutable_attribute(name: str):
    """
    Marks a certain attribute to be immutable
    """

    def annotation(target: typing.Type):
        _schedule_optimisation(target)
        return target

    return annotation


def all_immutable_attributes():
    """
    Marks all attributes to be immutable
    """

    def annotation(target: typing.Type):
        _schedule_optimisation(target)
        return target

    return annotation


def constant_global():
    """
    Marks the method as mutating only the internal state of the class / object, no global
    variables
    This can lead to optimisations into caching globals around the code
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target)
        return target

    return annotation


def inline_call(
    call_target: str, static_target: typing.Callable[[], typing.Callable] = None
):
    """
    Marks the calls to the given method to be inlined
    The optimiser has the last word on this and may choose
    different ways of optimising this

    'static_target' might be a callable returning a method
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target).code_walkers.append(
            MethodInlineProcessor(call_target, static_target)
        )
        return target

    return annotation


def eval_static(call_target: str):
    """
    Marks the call to the given method as a static eval-ed one
    Useful for configuration values
    Can only be used in some special cases where the arguments of the method call are known at
    optimisation time, e.g. using only constants

    WARNING: the value will be replaced by a static value, which is copy.deepcopy()-ed (when needed)
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target)
        return target

    return annotation


def eval_instance_static(call_target: str, allow_ahead_of_time=True):
    """
    Marks the call to the given method as a static eval-ed ones for each instance of the class

    Can only be used in some special cases where the arguments of the method call are known at
    optimisation time, e.g. using only constants

    The optimiser may choose to calculate the value of the expression ahead of time for each instance, meaning
    an injection into the constructor. This behaviour can be disabled via allow_ahead_of_time=False

    WARNING: the value will be replaced by a static value, which is copy.deepcopy()-ed (when needed)
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target)
        return target

    return annotation


def invalidate_cache(function, call_target: str, obj=None):
    pass


def access_static(name: str):
    """
    Accesses a variable (likely a global one) at optimisation time
    and puts it in the bytecode as a constant

    'name' can be a tree like shared.IS_CLIENT
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target)
        return target

    return annotation


def try_optimise():
    """
    Tries to optimise the given method
    Above annotations will also use this annotation by default
    """

    def annotation(target: typing.Callable):
        _schedule_optimisation(target)
        return target

    return annotation
