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
import types
import typing

import mcpython.mixin.PyBytecodeManipulator


class AbstractMixinProcessor:
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
    """

    def __init__(self, processor_name: str, skip_on_fail=False, priority=0):
        self.processor_name = processor_name
        self.skip_on_fail = skip_on_fail
        self.priority = priority
        self.bound_mixin_processors: typing.Dict[
            str, typing.List[AbstractMixinProcessor]
        ] = {}

    def replace_function_body(
        self, access_str: str
    ) -> typing.Callable[[types.FunctionType], types.FunctionType]:
        def annotate(function):
            self.bound_mixin_processors.setdefault(access_str, []).append(
                MixinReplacementProcessor(function)
            )
            return function

        return annotate
