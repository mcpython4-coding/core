"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from abc import ABC

import mcpython.common.container.crafting.IRecipeType
from mcpython import shared, logger
import mcpython.client.rendering.gui.CraftingGridRecipeRenderer
from mcpython.common.container.ItemStack import ItemStack
import typing


def transform_to_item_stack(item, table: dict) -> list:
    """
    Transforms an item name from recipe to an valid item list to compare with
    :param item: the item name given
    :param table: optional: an table of items which were decoded previous
    :return: an transformed name list of (item name, amount)
    """
    if "item" in item:
        itemname = item["item"]
        if itemname not in shared.registry.get_by_name("minecraft:item").entries:
            if itemname not in shared.registry.get_by_name("minecraft:block").entries:
                return []
        return [(itemname, item["count"] if "count" in item else 1)]
    elif "tag" in item:  # have we an tag?
        return [("#" + item["tag"], item["count"] if "count" in item else 1)]
    elif type(item) == list:  # have we an list of items?
        values = [transform_to_item_stack(x, table) for x in item]
        value = []
        for v in values:
            value += v
        return value
    else:
        logger.println("can't cast '" + str(item) + "' to valid item-list")
        return []


class AbstractCraftingGridRecipe(
    mcpython.common.container.crafting.IRecipeType.IRecipe, ABC
):
    RECIPE_VIEW_PROVIDER = (
        mcpython.client.rendering.gui.CraftingGridRecipeRenderer.CraftingTableLikeRecipeViewRenderer()
    )

    def as_grid_for_view(
        self, max_size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        raise NotImplementedError()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.as_grid_for_view())


@shared.crafting_handler
class GridShaped(AbstractCraftingGridRecipe):
    RECIPE_NAMES = ["minecraft:crafting_shaped", "crafting_shaped"]

    @classmethod
    def from_data(cls, data: dict):
        pattern = data["pattern"]
        table = {}
        for item in data["key"]:
            item_list = transform_to_item_stack(data["key"][item], table)
            if len(item_list) == 0:
                return
            table[item] = item_list

        grid = {}
        for y, row in enumerate(pattern):
            for x, key in enumerate(row):
                if key != " ":
                    grid[(x, y)] = table[key]

        out = transform_to_item_stack(data["result"], table)
        if len(out) == 0:
            return

        return cls(grid, out[0])

    def __init__(
        self,
        inputs: typing.Dict[typing.Tuple[int, int], typing.Tuple[str, int]],
        output: typing.Tuple[str, int],
    ):
        super().__init__()
        self.inputs = inputs
        self.output = output
        sx = max(self.inputs, key=lambda x: x[0])[0] + 1
        sy = max(self.inputs, key=lambda x: x[1])[1] + 1
        self.bboxsize = (sx, sy)

    def register(self):
        shared.crafting_handler.crafting_recipes_shaped.setdefault(
            len(self.inputs), {}
        ).setdefault(self.bboxsize, []).append(self)

    def as_grid(self):
        grid: typing.List[
            typing.List[typing.Optional[typing.List[typing.Tuple[str, int]]]]
        ] = [[None for _ in range(self.bboxsize[1])] for _ in range(self.bboxsize[0])]
        for x, y in self.inputs:
            grid[x][y] = self.inputs[x, y]

        return grid

    def as_grid_for_view(
        self, max_size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        grid = [
            [
                sum(
                    [
                        [ItemStack(*e)]
                        if not e[0].startswith("#")
                        else self.tag_to_stacks(*e)
                        for e in entry
                    ],
                    [],
                )
                if entry is not None
                else None
                for entry in row
            ]
            for row in self.as_grid()
        ]
        return grid, ItemStack(*self.output)

    @classmethod
    def tag_to_stacks(cls, name: str, count: int = None):
        return [
            ItemStack(e) for e in shared.tag_handler.get_entries_for(name, "blocks")
        ]


@shared.crafting_handler
class GridShapeless(AbstractCraftingGridRecipe):
    RECIPE_NAMES = ["minecraft:crafting_shapeless", "crafting_shapeless"]

    @classmethod
    def from_data(cls, data: dict):
        inputs = [transform_to_item_stack(x, {}) for x in data["ingredients"]]
        out = transform_to_item_stack(data["result"], {})
        if any([len(x) == 0 for x in inputs]) or len(out) == 0:
            return
        return cls(inputs, out[0])

    def __init__(
        self,
        inputs: typing.List[typing.List[typing.Tuple[str, int]]],
        output: typing.Tuple[str, int],
    ):
        super().__init__()
        self.inputs = inputs
        self.output = output

    def register(self):
        shared.crafting_handler.crafting_recipes_shapeless.setdefault(
            len(self.inputs), []
        ).append(self)

    def as_grid_for_view(
        self, max_size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        stacks = self.inputs[:]
        grid = [
            [
                sum(
                    [
                        [ItemStack(*e)]
                        if not e[0].startswith("#")
                        else GridShaped.tag_to_stacks(*e)
                        for e in stacks.pop()
                    ],
                    [],
                )
                if len(stacks) > 0
                else None
                for _ in range(max_size[1])
            ]
            for _ in range(max_size[0])
        ]
        return grid, ItemStack(*self.output)
