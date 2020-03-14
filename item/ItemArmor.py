"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import item.ItemTool


class ItemArmor(item.ItemTool.ItemTool):  # todo: change to IItemWithDamageBar-class
    def getDefensePoints(self):
        return 0

    def get_max_stack_size(self) -> int: return 1

