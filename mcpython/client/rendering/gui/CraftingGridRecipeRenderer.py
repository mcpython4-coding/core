import typing

import PIL.Image
import pyglet

import mcpython.client.gui.Slot
import mcpython.common.container.crafting.GridRecipeInstances as GridRecipe
import mcpython.common.container.crafting.IRecipeType
from mcpython.common.container.ItemStack import ItemStack
import mcpython.common.event.EventHandler
import mcpython.ResourceLoader
import mcpython.util.texture
from . import RecipeViewRenderer


class CraftingTableLikeRecipeViewRenderer(RecipeViewRenderer.AbstractRecipeViewRenderer):
    TEXTURE: typing.Optional[pyglet.image.AbstractImage] = None
    TEXTURE_SIZE: typing.Optional[typing.Tuple[int, int]] = None

    @classmethod
    def update_texture(cls):
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
        self.slots = [mcpython.client.gui.Slot.Slot() for _ in range(10)]
        self.enable_shapeless_symbol = False

    def prepare_for_recipe(
        self, recipe: mcpython.common.container.crafting.IRecipeType.IRecipe
    ):
        self.recipe = recipe
        if isinstance(recipe, GridRecipe.GridShaped):
            self.enable_shapeless_symbol = False
            i = 0
            for x in range(recipe.bboxsize[0]):
                for y in range(recipe.bboxsize[1]):
                    # todo: use all possibilities via an itertools.mutations() and tick system
                    item = recipe.inputs[x][y][0]
                    print(item)
                    self.slots[i].set_itemstack(ItemStack(*item))
                    i += 1

            self.slots[-1].set_itemstack(ItemStack(*recipe.output))

        elif isinstance(recipe, GridRecipe.GridShapeless):
            self.enable_shapeless_symbol = True

        return self

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
