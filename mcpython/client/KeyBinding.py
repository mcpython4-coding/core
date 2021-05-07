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

from mcpython.util.annotation import onlyInClient
from pyglet.window import key, mouse


@onlyInClient()
class KeyMouseBinding:
    """
    class holding an key or mouse binding
    """

    def __init__(
        self,
        name: str,
        group_name: str,
        default: typing.Union[int, typing.Iterable[int]],
        default_mod: typing.Union[int, typing.Iterable[int]] = 0,
    ):
        self.name = name
        self.group_name = group_name
        self.key_or_button = default
        self.mod = default_mod

    def applies(self, key_or_button: int, mod: int) -> bool:
        if type(self.key_or_button) in (list, set, tuple):
            if not all([key_or_button & b for b in self.key_or_button]):
                return False
        else:
            if not key_or_button & self.key_or_button:
                return False
        if type(self.mod) in (list, set, tuple):
            if not all([mod & b for b in self.mod]):
                return False
        else:
            if not mod & self.mod:
                return False
        return True
