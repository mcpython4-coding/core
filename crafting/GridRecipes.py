"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import crafting.IRecipeType
import globals as G
import gui.ItemStack


def transform_to_item_stack(item, table: dict) -> list:
    """
    transforms an item name from recipe to an valid item list to compare with
    :param item: the itemname given
    :param table: optional: an table of items which were decoded previous
    :return: an transformed name list of (itemname, amount)
    """
    if "item" in item:
        itemname = item["item"]
        if itemname not in G.registry.get_by_name("item").get_attribute("items"):
            if itemname not in G.registry.get_by_name("block").get_attribute("blocks"):
                return []
        return [(itemname, item["count"] if "count" in item else 1)]
    elif "tag" in item:  # have we an tag?
        entries = G.taghandler.taggroups["items"].tags["#"+item["tag"]].entries
        for item in entries[:]:
            if item not in G.registry.get_by_name("item").get_attribute("items"):
                if item not in G.registry.get_by_name("block").get_attribute("blocks"):
                    entries.remove(item)
        return entries
    elif type(item) == list:  # have we an list of items?
        values = [transform_to_item_stack(x, table) for x in item]
        value = []
        for v in values: value += v
        return value
    else:
        raise NotImplementedError("can't cast "+str(item)+" to valid itemlist")


@G.craftinghandler
class GridShaped(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_names() -> list:
        return ["minecraft:crafting_shaped", "crafting_shaped"]

    @classmethod
    def from_data(cls, data: dict):
        pattern = data["pattern"]
        table = {}
        for item in data["key"]:
            item_list = transform_to_item_stack(data["key"][item], table)
            if len(item_list) == 0: return
            table[item] = item_list
        grid = {}
        for y, row in enumerate(pattern):
            for x, key in enumerate(row):
                if key != " ": grid[(x, y)] = table[key]
        out = transform_to_item_stack(data["result"], table)
        if len(out) == 0: return
        return cls(grid, out[0])

    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output
        sx = max(self.inputs, key=lambda x: x[0])[0]
        sy = max(self.inputs, key=lambda x: x[1])[1]
        self.bboxsize = (sx, sy)

    def register(self):
        G.craftinghandler.crafting_recipes_shaped.setdefault(len(self.inputs), {}).setdefault(
            self.bboxsize, []).append(self)


@G.craftinghandler
class GridShapeless(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_names() -> list:
        return ["minecraft:crafting_shapeless", "crafting_shapeless"]

    @classmethod
    def from_data(cls, data: dict):
        inputs = [transform_to_item_stack(x, {}) for x in data["ingredients"]]
        out = transform_to_item_stack(data["result"], {})
        if any([len(x) == 0 for x in inputs]) or len(out) == 0: return
        return cls(inputs, out[0])

    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output

    def register(self):
        G.craftinghandler.crafting_recipes_shapeless.setdefault(len(self.inputs), []).append(self)

