"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
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

