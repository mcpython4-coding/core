"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.state.StatePart
import globals as G


class UIPart(mcpython.state.StatePart.StatePart):
    def __init__(self, position, bboxsize, anchor_element="WS", anchor_window="WS"):
        super().__init__()
        self.position = position
        self.bboxsize = bboxsize
        self.anchor_element = anchor_element
        self.anchor_window = anchor_window

    def get_real_position(self):
        x, y = self.position
        wx, wy = G.window.get_size()
        bx, by = self.bboxsize
        if self.anchor_element[0] == "M":
            x -= bx // 2
        elif self.anchor_element[0] == "E":
            x = bx - abs(x)
        if self.anchor_element[1] == "M":
            y -= by // 2
        elif self.anchor_element[1] == "N":
            y = by - abs(y)
        if self.anchor_window[0] == "M":
            x += wx // 2
        elif self.anchor_window[0] == "E":
            x = wx - abs(x)
        if self.anchor_window[1] == "M":
            y += wy // 2
        elif self.anchor_window[1] == "N":
            y = wy - abs(y)
        return x, y

