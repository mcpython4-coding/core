"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.crafting.IRecipeType
import globals as G
import mcpython.crafting.GridRecipes


@G.craftinghandler
class FurnesRecipe(mcpython.crafting.IRecipeType.IRecipe):
    @staticmethod
    def get_recipe_names() -> list:
        return ["minecraft:smelting", "minecraft:blasting", "minecraft:smoking"]

    @classmethod
    def from_data(cls, data: dict):
        inputs = [x[0] for x in mcpython.crafting.GridRecipes.transform_to_item_stack(data["ingredient"], {})]
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

