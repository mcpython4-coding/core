"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import crafting.IRecipeType
import globals as G
import gui.ItemStack


def transform_to_itemstack(item, table: dict) -> list:
    if "item" in item:
        return [gui.ItemStack.ItemStack(item["item"], amount=item["count"] if "count" in item else 1)]
    elif "tag" in item:  # have we an tag?
        # todo: implement
        return []
    elif type(item) == list:  # have we an list of items?
        values = [transform_to_itemstack(x, table) for x in item]
        value = []
        for v in values: value += v
        return value
    else:
        raise NotImplementedError("can't cast "+str(item)+" to valid itemlist")


@G.craftinghandler
class GridShaped(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_name() -> str:
        return "minecraft:crafting_shaped"

    @classmethod
    def from_data(cls, data: dict):
        pattern = data["pattern"]
        table = {}
        key: dict = data["key"]
        for item in key.keys():
            table[item] = transform_to_itemstack(key[item], table)
        grid = [[None] * len(pattern)] * len(pattern[0])
        for y, row in enumerate(pattern):
            for x, item in enumerate(pattern[0]):
                if item != " ": grid[x][y] = table[item]
        return cls(grid, transform_to_itemstack(data["result"], table)[0])

    def __init__(self, grid: list, output: gui.ItemStack, xp=0, enabled=True, on_craft=None, on_select=None):
        """
        creates an new recipe instance
        :param grid: the grid to use. is gui.ItemStack[[
        :param output: the item to use as output
        :param xp: the xp to give to player when crafted
        :param enabled: if the recipe should be arrival
        :param on_craft: function to be callen when item is crafted
        :param on_select: function to be callen when the player tries to craft this recipe
        """
        self.grid = grid
        self.output = output
        self.xp: float = xp
        self.enabled = enabled
        self.on_craft = on_craft
        self.on_select = on_select
        self.gridsize = (len(self.grid[0]), len(self.grid))

    def get_identification(self):
        return ([self.output.item.get_name()] if self.output.item else []) + [(len(self.grid[0]), len(self.grid))]


@G.craftinghandler
class GridShapeless(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_name() -> str:
        return "minecraft:crafting_shapeless"

    @classmethod
    def from_data(cls, data: dict):
        inputs = []
        for item in data["ingredients"]:
            inputs.append(transform_to_itemstack(item, {}))
        output = transform_to_itemstack(data["result"], {})[0]
        # if output.item and output.item.get_name() == "minecraft:redstone":
        #     print(data["ingredients"], data["result"], output.amount)
        return cls(inputs, output)

    def __init__(self, inputs: list, output: gui.ItemStack.ItemStack, xp=0, enabled=True, on_craft=None,
                 on_select=None):
        """
        creates an new recipe instance
        :param inputs: an list of slots that should be used as inputs
        :param output: the item to use as output
        :param xp: the xp to give to player when crafted
        :param enabled: if the recipe should be arrival
        :param on_craft: function to be callen when item is crafted
        :param on_select: function to be callen when the player tries to craft this recipe
        """
        self.inputs = inputs
        self.output = output
        self.xp = xp
        self.enabled = enabled
        self.on_craft = on_craft
        self.on_select = on_select

    def get_identification(self):
        return ([self.output.item.get_name()] if self.output.item else []) + [len(self.inputs)]

