"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing
from abc import ABC

import mcpython.common.container.crafting.IRecipe
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.engine import logger

if shared.IS_CLIENT:
    import mcpython.client.rendering.gui.CraftingGridRecipeRenderer


def transform_to_item_stack(item, file: str) -> typing.List[typing.Tuple[str, int]]:
    """
    Transforms an item name from recipe to a valid item list to compare with
    :param item: the item name given
    :param file: the file currently in
    :return: an transformed name list of (item name, amount)
    """
    if "item" in item:
        item_name = item["item"]
        if item_name not in shared.registry.get_by_name("minecraft:item").full_entries:
            if (
                item_name
                not in shared.registry.get_by_name("minecraft:block").full_entries
            ):
                return []
        return [(item_name, item["count"] if "count" in item else 1)]

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
    __slots__ = mcpython.common.container.crafting.IRecipe.IRecipe.__slots__ + (
        "grid_hash",
    )

    RECIPE_VIEW = (
        mcpython.client.rendering.gui.CraftingGridRecipeRenderer.CraftingTableLikeRecipeViewRenderer()
    )
    CRAFTING_SUPPORT = ["minecraft:crafting_table"]

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
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        raise NotImplementedError()

    def __repr__(self):
        return "{}(name={},{})".format(
            self.__class__.__name__, self.name, self.as_grid_for_view()
        )


@shared.crafting_handler
class GridShaped(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_shaped", "crafting_shaped"]

    __slots__ = AbstractCraftingGridRecipe.__slots__ + (
        "inputs",
        "outputs",
        "bounding_box_size",
    )

    @classmethod
    def from_data(cls, data: dict, file: str):
        pattern = data["pattern"]
        table: typing.Dict[
            typing.Tuple[int, int], typing.List[typing.Tuple[str, int]]
        ] = {}
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
        inputs: typing.Dict[
            typing.Tuple[int, int], typing.List[typing.Tuple[str, int]]
        ],
        output: typing.Tuple[str, int],
    ):
        super().__init__()
        self.inputs = inputs
        self.output = output
        sx = max(self.inputs, key=lambda x: x[0])[0] + 1
        sy = max(self.inputs, key=lambda x: x[1])[1] + 1
        self.bounding_box_size = (sx, sy)

    async def prepare(self):
        shared.crafting_handler.crafting_recipes_shaped.setdefault(
            len(self.inputs), {}
        ).setdefault(self.bounding_box_size, []).append(self)

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

    __slots__ = AbstractCraftingGridRecipe.__slots__ + ("inputs", "outputs")

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

    async def prepare(self):
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


@shared.crafting_handler
class ArmorDyeRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_armordye"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class BannerDuplicateRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_bannerduplicate"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class BookCloningRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_bookcloning"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class FireworkRocketRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_firework_rocket"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class FireworkStarRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_firework_star"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class FireworkStarFadeRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_firework_star_fade"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class MapCloningRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_mapcloning"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class MapExtendingRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_mapextending"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class RepairItemRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_repairitem"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class ShieldDecoration(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_shielddecoration"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class ShulkerboxColoringRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_shulkerboxcoloring"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[ItemStack]]], ItemStack | None
    ]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class SuspiciousStewRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_suspiciousstew"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()


@shared.crafting_handler
class TippedArrowRecipe(AbstractCraftingGridRecipe):
    RECIPE_TYPE_NAMES = ["minecraft:crafting_special_tippedarrow"]

    def as_grid_for_view(
        self, size=(3, 3)
    ) -> typing.Tuple[typing.List[typing.List[typing.List[ItemStack]]], ItemStack]:
        return [], None

    @classmethod
    def from_data(cls, data: dict, file: str):
        return cls()
