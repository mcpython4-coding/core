"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.client.gui.crafting.GridRecipes
import deprecation


@deprecation.deprecated("dev2-2", "a1.5.0")
class ShapedCraftingRecipeFactory:
    @deprecation.deprecated("dev2-2", "a1.5.0")
    def __init__(self, output):
        self.grid = {}
        self.output = output

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def set_input(self, position, itemname):
        if type(itemname) == str:
            itemname = [itemname]
        for pos in position if type(position) == list else [position]:
            self.grid[pos] = itemname
        return self

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def finish(self):
        mcpython.client.gui.crafting.GridRecipes.GridShaped(
            self.grid, self.output
        ).register()


@deprecation.deprecated("dev2-2", "a1.5.0")
class ShapelessCraftingRecipeFactory:
    @deprecation.deprecated("dev2-2", "a1.5.0")
    def __init__(self, output):
        self.output = output
        self.items = []

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def add_item(self, item, count=1):
        if type(item) == str:
            item = [item]
        self.items += [item] * count
        return self

    @deprecation.deprecated("dev2-2", "a1.5.0")
    def finish(self):
        mcpython.client.gui.crafting.GridRecipes.GridShapeless(self.items, self.output)
