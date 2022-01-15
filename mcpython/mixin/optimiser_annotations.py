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


def constant_arg(name: str):
    """
    Promises that the given arg will not be modified
    Only affects mutable data types
    Removes the need to copy the data during inlining
    """

    def annotation(target: typing.Callable):
        return target

    return annotation


def constant_operation():
    """
    Promises that the method will not affect the state of the system, meaning it is e.g.
    a getter method
    """

    def annotation(target: typing.Callable):
        return target

    return annotation


def mutable_attribute(name: str):
    """
    Marks a certain attribute to be mutable
    Only affects when all_immutable_attributes() is used also on the class
    """

    def annotation(target: typing.Callable):
        return target

    return annotation


def immutable_attribute(name: str):
    """
    Marks a certain attribute to be immutable
    """

    def annotation(target: typing.Callable):
        return target

    return annotation


def all_immutable_attributes():
    """
    Marks all attributes to be immutable
    """

    def annotation(target: typing.Callable):
        return target

    return annotation


def constant_global():
    """
    Marks the method as mutating only the internal state of the class / object, no global
    variables
    This can lead to optimisations into caching globals around the code
    """

    def annotation(target: typing.Callable):
        return target

    return annotation
