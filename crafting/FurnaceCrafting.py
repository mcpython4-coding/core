import crafting.IRecipeType
import globals as G
import crafting.GridRecipes


@G.craftinghandler
class FurnesRecipe(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_names() -> list:
        return ["minecraft:smelting", "smelting"]

    @classmethod
    def from_data(cls, data: dict):
        inputs = [x[0] for x in crafting.GridRecipes.transform_to_item_stack(data["ingredient"], {})]
        result = data["result"]
        return cls(inputs, result, data["experience"], data["cookingtime"] / 20)

    def __init__(self, i, o, xp, time):
        self.input = i
        self.output = o
        self.xp = xp
        self.time = time

    def register(self):
        [G.craftinghandler.furnace_recipes.setdefault(e, self) for e in self.input]

