import typing

import PIL.Image
import pyglet

import mcpython.client.gui.Slot
import mcpython.common.container.crafting.GridRecipeInstances as GridRecipe
import mcpython.common.container.crafting.IRecipeType
from mcpython import logger
from mcpython.common.container.ItemStack import ItemStack
import mcpython.common.event.EventHandler
import mcpython.ResourceLoader
import mcpython.util.texture
from . import RecipeViewRenderer


class CraftingTableLikeRecipeViewRenderer(
    RecipeViewRenderer.AbstractRecipeViewRenderer
):
    TEXTURE: typing.Optional[pyglet.image.AbstractImage] = None
    TEXTURE_SIZE: typing.Optional[typing.Tuple[int, int]] = None

    @classmethod
    def update_texture(cls):
        # the custom view background
        texture = mcpython.ResourceLoader.read_image(
            "minecraft:gui/container/crafting_table_view"
        )

        size = texture.size
        texture = texture.crop((0, 0, 176 / 255 * size[0], 71 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture)
        cls.TEXTURE_SIZE = texture.size

    def __init__(self):
        self.recipe = None
        self.slots = [
            mcpython.client.gui.Slot.Slot(
                allow_player_insert=False,
                allow_player_remove=False,
                allow_player_add_to_free_place=False,
            )
            for _ in range(10)
        ]
        self.enable_shapeless_symbol = False

    def prepare_for_recipe(
        self, recipe: mcpython.common.container.crafting.IRecipeType.IRecipe
    ):
        self.recipe = recipe

        if isinstance(recipe, GridRecipe.AbstractCraftingGridRecipe):
            grid, output = recipe.as_grid_for_view((3, 3))
            i = 0
            for x, row in enumerate(grid):
                for y, entries in enumerate(row):
                    if entries is None:
                        self.slots[i].itemstack.clean()
                    else:
                        self.slots[i].set_itemstack(entries[0])
                    i += 1
            self.slots[-1].set_itemstack(output)
        else:
            logger.println(
                "[ERROR] fatal recipe view exception: recipe is no grid recipe"
            )
            self.clear()
            return self

        return self

    def clear(self):
        [slot.itemstack.clean() for slot in self.slots]

    def draw(self, position: typing.Tuple[int, int], hovering_slot=None):
        self.TEXTURE.blit(*position)
        for slot in self.slots:
            slot.draw(*position, hovering=slot == hovering_slot)
            slot.draw_label()

    def add_to_batch(
        self, position: typing.Tuple[int, int], batch: pyglet.graphics.Batch
    ):
        raise NotImplementedError

    def get_rendering_size(self) -> typing.Tuple[int, int]:
        return self.TEXTURE_SIZE

    def get_slots(self):
        return self.slots


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", CraftingTableLikeRecipeViewRenderer.update_texture
)
