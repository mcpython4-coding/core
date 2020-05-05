"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import crafting.GridRecipes


class ShapedCraftingRecipeFactory:
    def __init__(self, output):
        self.grid = {}
        self.output = output

    def set_input(self, position, itemname):
        if type(itemname) == str: itemname = [itemname]
        for pos in (position if type(position) == list else [position]): self.grid[pos] = itemname
        return self

    def finish(self):
        crafting.GridRecipes.GridShaped(self.grid, self.output).register()


class ShapelessCraftingRecipeFactory:
    def __init__(self, output):
        self.output = output
        self.items = []

    def add_item(self, item, count=1):
        if type(item) == str: item = [item]
        self.items += [item] * count
        return self

    def finish(self):
        crafting.GridRecipes.GridShapeless(self.items, self.output)

