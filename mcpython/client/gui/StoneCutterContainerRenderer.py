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
import math

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.InventoryChest
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.ResourceStack
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
import PIL
import pyglet
from mcpython import shared
from mcpython.client.rendering.ui.Scrollbar import ScrollbarRenderer
from mcpython.common.container.crafting.StonecuttingRecipe import StoneCuttingRecipe
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.engine import logger
from pyglet.window import mouse


class StoneCutterContainerRenderer(
    mcpython.client.gui.ContainerRenderer.ContainerRenderer
):
    """
    Inventory class for the stone cutter
    May be shared across multiple stonecutters at client side
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    SCROLLBAR_TEXTURE = None

    @classmethod
    def update_texture(cls):
        import mcpython.util.texture

        texture = mcpython.engine.ResourceLoader.read_image(
            "minecraft:gui/container/stonecutter"
        )
        size = texture.size
        texture_main = texture.crop((0, 0, 175 / 255 * size[0], 165 / 255 * size[1]))
        size_main = texture_main.size
        texture_main = texture_main.resize(
            (size_main[0] * 2, size_main[1] * 2), PIL.Image.NEAREST
        )
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture_main)
        cls.TEXTURE_SIZE = texture_main.size

        texture_scrollbar = texture.crop(
            (176, 0, 188 / 255 * size[0], 15 / 255 * size[1])
        )
        size_scrollbar = texture_scrollbar.size
        texture_scrollbar = texture_scrollbar.resize(
            (size_scrollbar[0] * 2, size_scrollbar[1] * 2), PIL.Image.NEAREST
        )
        cls.SCROLLBAR_TEXTURE = mcpython.util.texture.to_pyglet_image(texture_scrollbar)

    def __init__(self):
        super().__init__()
        if self.custom_name is None:
            self.custom_name = "Stonecutter"

        self.currently_selected = -1
        self.previous_item = None
        self.possible_outputs = []
        self.scrollbar = ScrollbarRenderer(
            self.SCROLLBAR_TEXTURE,
            (2 * 119, 2 * 97),
            2 * (69 - 15) - self.SCROLLBAR_TEXTURE.height,
            1,
            on_progress_change=self.update_selection_slots,
        )

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_stonecutter.json"

    async def on_activate(self):
        await super().on_activate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    async def on_deactivate(self):
        await super().on_deactivate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    # todo: move to container
    async def create_slot_renderers(self) -> list:
        # 3 rows of 9 slots of storage
        return (
            [mcpython.client.gui.Slot.Slot(on_update=self.update_selection_view)]
            + [
                mcpython.client.gui.Slot.Slot(
                    allow_player_remove=False,
                    allow_player_insert=False,
                    enable_hovering_background=False,
                    allow_half_getting=False,
                    on_click_on_slot=self.handle_slot_click,
                )
                for _ in range(3 * 4)
            ]
            + [
                mcpython.client.gui.Slot.Slot(
                    on_update=self.update_output_slot, allow_half_getting=False
                )
            ]
        )

    def handle_slot_click(self, slot, button, modifiers):
        index = self.slots.index(slot) - 1

        if button == mouse.LEFT:
            self.currently_selected = index
            self.slots[-1].set_itemstack(slot.get_itemstack().copy())

    def draw(self, hovering_slot=None):
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        self.bg_image_size = self.TEXTURE_SIZE
        self.scrollbar.draw((x, y))
        super().draw(hovering_slot)

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventory_main.slots[:36] + self.slots

    async def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            await shared.inventory_handler.hide(self)

    def update_shift_container(self):
        shared.inventory_handler.shift_container_handler.container_A = (
            shared.world.get_active_player().inventory_main.slots[:36]
        )
        shared.inventory_handler.shift_container_handler.container_B = [
            self.slots[0],
            self.slots[-1],
        ]

    def update_selection_view(self, player=None):
        item = self.slots[0].get_itemstack().get_item_name()

        if item == self.previous_item:
            return

        self.previous_item = item

        if not item or item not in StoneCuttingRecipe.RECIPES:
            self.possible_outputs.clear()

            for slot in self.slots[1:]:
                slot.get_itemstack().clean()

            self.scrollbar.steps = 1
            self.scrollbar.current_step = 0
            self.currently_selected = -1
            return

        self.possible_outputs = [
            (recipe.result, recipe.count) for recipe in StoneCuttingRecipe.RECIPES[item]
        ]
        self.scrollbar.steps = max(math.ceil(len(self.possible_outputs) / 9) - 2, 1)
        self.scrollbar.current_step = min(
            self.scrollbar.current_step, self.scrollbar.steps - 1
        )

        self.update_selection_slots()

    def update_selection_slots(self):
        for slot in self.slots[1:-1]:
            slot.get_itemstack().clean()

        offset = self.scrollbar.current_step * 4

        for y in range(3):
            for x in range(4):
                i = offset + x + y * 4
                slot = self.slots[x + y * 4 + 1]

                if i >= len(self.possible_outputs) - 1:
                    return

                try:
                    slot.set_itemstack(ItemStack(*self.possible_outputs[i]))
                except IndexError:
                    logger.print_exception(
                        str((i, len(self.possible_outputs), x, y, slot, offset))
                    )

    def update_output_slot(self, player=None):
        if self.slots[-1].get_itemstack().is_empty() and self.currently_selected != -1:
            self.slots[0].get_itemstack().add_amount(-1)
            self.update_selection_view()


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", StoneCutterContainerRenderer.update_texture
)
