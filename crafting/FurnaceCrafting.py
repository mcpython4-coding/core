"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import crafting.IRecipeType
import globals as G
import crafting.GridRecipes


@G.craftinghandler
class FurnesRecipe(crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_names() -> list:
        return ["minecraft:smelting", "minecraft:blasting", "minecraft:smoking"]

    @classmethod
    def from_data(cls, data: dict):
        inputs = [x[0] for x in crafting.GridRecipes.transform_to_item_stack(data["ingredient"], {})]
        result = data["result"]
        return cls(data["type"], inputs, result, data["experience"], data["cookingtime"] / 20)

    def __init__(self, t, i, o, xp, time):
        super().__init__()
        self.input = i
        self.output = o
        self.xp = xp
        self.time = time
        self.type = t

    def register(self):
        [G.craftinghandler.furnace_recipes.setdefault(self.type, {}).setdefault(e, self) for e in self.input]

