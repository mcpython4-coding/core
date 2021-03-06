"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from abc import ABC

import mcpython.common.container.crafting.IRecipe
from mcpython import shared, logger
import mcpython.client.rendering.gui.CraftingGridRecipeRenderer
from mcpython.common.container.ItemStack import ItemStack
import typing


def transform_to_item_stack(item, file: str) -> list:
    """
    Transforms an item name from recipe to a valid item list to compare with
    :param item: the item name given
    :param file: the file currently in
    :return: an transformed name list of (item name, amount)
    """
    assert not isinstance(file, dict), "function updated; please update code"

    if "item" in item:
        itemname = item["item"]
        if itemname not in shared.registry.get_by_name("minecraft:item").entries:
            if itemname not in shared.registry.get_by_name("minecraft:block").entries:
                return []
        return [(itemname, item["count"] if "count" in item else 1)]

    elif "tag" in item:  # have we a tag?
        return [("#" + item["tag"], item["count"] if "count" in item else 1)]

    elif type(item) == list:  # have we a list of items?
        values = [transform_to_item_stack(x, file) for x in item]
        value = []
        for v in values:
            value += v
        return value

    else:
        # todo: add injection point for custom data
        logger.println(
            "can't cast '{}' in file '{}' to valid item-list".format(item, file)
        )
        return []


class AbstractCraftingGridRecipe(
    mcpython.common.container.crafting.IRecipe.IRecipe, ABC
):
    RECIPE_VIEW = (
        mcpython.client.rendering.gui.CraftingGridRecipeRenderer.CraftingTableLikeRecipeViewRenderer()
    )

    def __init__(self):
        super().__init__()
        self.grid_hash = None

    def __hash__(self):
        if self.grid_hash is None:
            self.grid_hash = self.calculate_hash()

        return self.grid_hash

    def calculate_hash(self) -> int:
        grid, output = self.as_grid_for_view()
        data = (
            tuple(
                (
                    tuple(
                        (
                            tuple(
                                (
                                    (itemstack.get_item_name(), itemstack.amount)
                                    for itemstack in items
                                )
                            )
                            for items in row
                        )
                    )
                    for row in grid
                )
            ),
            (output.get_item_name(), output.amount),
        )
        return hash(data)

    def __eq__(self, other):
        return (
            isinstance(other, AbstractCraftingGridRecipe)
            and self.as_grid_for_view() == other.as_grid_for_view()
        )

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        raise NotImplementedError()

    def __repr__(self):
        return "{}(name={},{})".format(
            self.__class__.__name__, self.name, self.as_grid_for_view()
        )


@shared.crafting_handler
class GridShaped(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_shaped", "crafting_shaped"]

    @classmethod
    def from_data(cls, data: dict, file: str):
        pattern = data["pattern"]
        table = {}
        for item in data["key"]:
            item_list = transform_to_item_stack(data["key"][item], file)
            if len(item_list) == 0:
                return
            table[item] = item_list

        grid = {}
        for y, row in enumerate(pattern):
            for x, key in enumerate(row):
                if key != " ":
                    grid[(x, y)] = table[key]

        out = transform_to_item_stack(data["result"], file)
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

    def prepare(self):
        shared.crafting_handler.crafting_recipes_shaped.setdefault(
            len(self.inputs), {}
        ).setdefault(self.bboxsize, []).append(self)

    def as_grid(self, size=(3, 3)):
        grid: typing.List[
            typing.List[typing.Optional[typing.List[typing.Tuple[str, int]]]]
        ] = [[None for _ in range(size[1])] for _ in range(size[0])]
        for x, y in self.inputs:
            grid[x][y] = self.inputs[x, y]

        return grid

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        grid = [
            [
                sum(
                    [
                        [ItemStack(*e)]
                        if not e[0].startswith("#")
                        else self.tag_to_stacks(*e, recipe_name=self.name)
                        for e in entry
                    ],
                    [],
                )
                if entry is not None
                else None
                for entry in row
            ]
            for row in self.as_grid(size)
        ]
        return grid, ItemStack(*self.output)

    @classmethod
    def tag_to_stacks(cls, name: str, count: int = None, recipe_name=None):
        try:
            tags = shared.tag_handler.get_tag_for(name, "items")
        except ValueError:
            logger.println(
                "[ERROR] could not load tag '{}' for recipe '{}'".format(
                    name, recipe_name
                )
            )
            return []
        return list(map(ItemStack, tags.entries))


@shared.crafting_handler
class GridShapeless(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_shapeless", "crafting_shapeless"]

    @classmethod
    def from_data(cls, data: dict, file: str):
        inputs = [transform_to_item_stack(x, file) for x in data["ingredients"]]
        out = transform_to_item_stack(data["result"], file)
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

    def prepare(self):
        shared.crafting_handler.crafting_recipes_shapeless.setdefault(
            len(self.inputs), []
        ).append(self)

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        stacks = self.inputs[:]
        grid = [
            [
                sum(
                    [
                        [ItemStack(*e)]
                        if not e[0].startswith("#")
                        else GridShaped.tag_to_stacks(*e, recipe_name=self.name)
                        for e in stacks.pop()
                    ],
                    [],
                )
                if len(stacks) > 0
                else None
                for _ in range(size[1])
            ]
            for _ in range(size[0])
        ]
        return grid, ItemStack(*self.output)
