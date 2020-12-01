"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.item.Item


class ItemTool(mcpython.common.item.Item.Item):
    NAME = "minecraft:unknown_tool"

    HAS_BLOCK = False
    STACK_SIZE = 1

    TOOL_LEVEL = 0
    TOOL_TYPE = []

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        if not issubclass(type(other), ItemTool): return False
        return other.NAME == self.NAME

    def get_tool_level(self):  # todo: remove
        return self.TOOL_LEVEL

    def get_tool_type(self):  # todo: remove
        return self.TOOL_TYPE

    def get_speed_multiplyer(self, itemstack):
        return 1

