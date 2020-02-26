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

    @staticmethod
    def has_block() -> bool:
        return False

    def __init__(self):
        super().__init__()

    def get_max_stack_size(self) -> int:
        return 1

    def __eq__(self, other):
        if not issubclass(type(other), ItemTool): return False
        return other.NAME == self.NAME

    def get_tool_level(self):
        return 0

    def get_tool_type(self):
        return []

    def get_speed_multiplyer(self, itemstack):
        return 1

