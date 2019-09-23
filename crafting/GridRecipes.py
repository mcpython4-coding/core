"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import crafting.IRecipeType
import globals as G
import gui.ItemStack


def transform_to_itemstack(item, table: dict) -> list:
    """
    transforms an item name from recipe to an valid item list to compare with
    :param item: the itemname given
    :param table: optional: an table of items which were decoded previous
    :return: an transformed name list of (itemname, amount)
    """
    if "item" in item:
        return [(item["item"], item["count"] if "count" in item else 1)]
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
        for item in data["key"]:
            table[item] = transform_to_itemstack(data["key"][item], table)
        grid = {}
        for y, row in enumerate(pattern):
            for x, key in enumerate(row):
                if key != " ": grid[(x, y)] = table[key]
        return cls(grid, transform_to_itemstack(data["result"], table)[0])

    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output

    def register(self):
        G.craftinghandler.crafting_recipes.setdefault(len(self.inputs), []).append(self)


@G.craftinghandler
class GridShapeless(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_name() -> str:
        return "minecraft:crafting_shapeless"

    @classmethod
    def from_data(cls, data: dict):
        inputs = [transform_to_itemstack(x, {}) for x in data["ingredients"]]
        return cls(inputs, transform_to_itemstack(data["result"], {})[0])

    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output

    def register(self):
        G.craftinghandler.crafting_recipes.setdefault(len(self.inputs), []).append(self)

