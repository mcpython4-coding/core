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
# TODO: export this to the client backend
# CallbackHelper removed as functools.partial is the same


class IEventInfo:
    """
    Base class for every event info declared here
    """

    def equals(self, *args):
        raise NotImplementedError()


class KeyPressEventInfo(IEventInfo):
    """
    info for key press
    """

    def __init__(self, symbol: int, modifier=None):
        if modifier is None:
            modifier = []
        self.symbol = symbol
        self.modifier = modifier

    def equals(self, symbol, modifiers):
        return symbol == self.symbol and all([modifiers & x for x in self.modifier])


class MousePressEventInfo(IEventInfo):
    """
    Info for mouse press
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
