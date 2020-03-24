"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import item.Item
import enum
from util.enums import ToolType


class ItemTool(item.Item.Item):
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

