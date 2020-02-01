"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import item.Item
import enum


class ToolType(enum.Enum):
    HAND = 0
    PICKAXE = 1
    AXE = 2
    SHOVEL = 3
    SHEAR = 4
    SWORD = 5  # not real an tool, but internally handled as one of it
    HOE = 6  # not real an tool, but internally handled as one of it


class ItemTool(item.Item.Item):
    @staticmethod
    def get_name() -> str:
        return "minecraft:unknown_tool"

    @staticmethod
    def has_block() -> bool:
        return False

    def __init__(self):
        super().__init__()

    def get_max_stack_size(self) -> int:
        return 1

    def __eq__(self, other):
        if not issubclass(type(other), ItemTool): return False
        return other.get_name() == self.get_name()

    def get_tool_level(self):
        return 0

    def get_tool_type(self):
        return []

    def get_speed_multiplyer(self, itemstack):
        return 1

