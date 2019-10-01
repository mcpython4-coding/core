"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import item.Item


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

    def get_brake_time_for(self, block):
        pass

