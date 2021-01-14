"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from pyglet.window import key, mouse
import typing
from mcpython.util.annotation import onlyInClient


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
