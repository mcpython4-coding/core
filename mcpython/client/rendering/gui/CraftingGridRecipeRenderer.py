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
import itertools
import typing

import mcpython.client.gui.Slot
import mcpython.common.container.crafting.GridRecipeInstances as GridRecipe
import mcpython.common.container.crafting.IRecipe
import mcpython.common.event.EventHandler
import mcpython.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import logger

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

        i = 0
        for x in range(3):
            for y in range(3):
                self.slots[i].position = (x * 36 + 58, (2 - y) * 36 + 18)
                i += 1
        self.slots[-1].position = (246, 54)

        self.mutation_iterator = []
        self.grid = None
        self.enable_shapeless_symbol = False

        self.remaining_state_time = 0

    def prepare_for_recipe(
        self, recipe: mcpython.common.container.crafting.IRecipe.IRecipe
    ):
        self.recipe = recipe
        self.clear()

        if isinstance(recipe, GridRecipe.AbstractCraftingGridRecipe):
            self.mutation_iterator.clear()

            self.grid, output = recipe.as_grid_for_view((3, 3))
            i = 0
            for row in self.grid:
                for entry in row:
                    if entry is not None and len(entry) > 0:
                        self.slots[i].set_itemstack(entry[0])
                        self.mutation_iterator.append(
                            itertools.cycle(range(len(entry)))
                        )
                    else:
                        self.mutation_iterator.append(tuple())
                    i += 1
            self.slots[-1].set_itemstack(output)
        else:
            logger.println(
                "[ERROR] fatal recipe view exception: recipe is not a grid recipe. Implement "
                "AbstractCraftingGridRecipe for making this view work!"
            )
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

    def tick(self, dt: float):
        self.remaining_state_time -= dt
        if self.remaining_state_time <= 0:
            self.remaining_state_time += 1
            i = 0
            for x, row in enumerate(self.grid):
                for y, entries in enumerate(row):
                    if entries is not None and len(entries) > 0:
                        self.slots[i].set_itemstack(
                            entries[next(self.mutation_iterator[i])]
                        )
                    i += 1


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", CraftingTableLikeRecipeViewRenderer.update_texture
)
