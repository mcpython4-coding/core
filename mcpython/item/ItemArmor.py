"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.item.ItemTool


class ItemArmor(mcpython.item.ItemTool.ItemTool):  # todo: change to IItemWithDamageBar-class
    DEFENSE_POINTS = 0

    def getDefensePoints(self):  # todo: remove
        return self.DEFENSE_POINTS

    STACK_SIZE = 1

