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


class MousePressEventInfo:
    """
    Info for mouse press
    todo: remove this
    """

    def __init__(self, mouse: int, modifier=None, area=None):
        if modifier is None:
            modifier = []
        self.mouse = mouse
        self.modifier = modifier
        self.area = area

    def equals(self, x, y, button, modifiers):
        return (
            button == self.mouse
            and all([modifiers & x for x in self.modifier])
            and (
                (
                    self.area[0][0] <= x <= self.area[1][0]
                    and self.area[0][1] <= y <= self.area[1][1]
                )
                if self.area
                else True
            )
        )
