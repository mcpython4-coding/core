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
import time
import typing

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.FurnaceCraftingHelper
import mcpython.common.container.ResourceStack
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class InventoryFurnaceRenderer(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    Inventory renderer class for the furnace

    todo: move a LOT of stuff to the container
    """

    # The texture properties, provided when reloading
    TEXTURE_BG = None
    TEXTURE_BG_SIZE = None
    TEXTURE_ARROW = None
    TEXTURE_ARROW_SIZE = None
    TEXTURE_FIRE = None
    TEXTURE_FIRE_SIZE = None

    @classmethod
    async def update_texture(cls):
        texture = await mcpython.engine.ResourceLoader.read_image(
            "minecraft:gui/container/furnace"
        )
        size = texture.size

        texture_bg = texture.crop((0, 0, 175 / 255 * size[0], 166 / 255 * size[1]))
        size = texture_bg.size
        texture_bg = texture_bg.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        cls.TEXTURE_BG = mcpython.util.texture.to_pyglet_image(texture_bg)
        cls.TEXTURE_BG_SIZE = texture_bg.size

        texture_arrow = texture.crop(
            (
                176 / 255 * size[0],
                14 / 255 * size[1],
                200 / 255 * size[0],
                31 / 255 * size[1],
            )
        )
        texture_arrow_size = texture_arrow.size
        texture_arrow = texture_arrow.resize(
            (texture_arrow_size[0] * 2, texture_arrow_size[1] * 2), PIL.Image.NEAREST
        )
        cls.TEXTURE_FIRE = mcpython.util.texture.to_pyglet_image(texture_arrow)
        cls.TEXTURE_FIRE_SIZE = texture_arrow.size

        texture_fire = texture.crop(
            (176 / 255 * size[0], 0, 190 / 255 * size[0], 14 / 255 * size[1])
        )
        texture_fire_size = texture_fire.size
        texture_fire = texture_fire.resize(
            (texture_fire_size[0] * 2, texture_fire_size[1] * 2), PIL.Image.NEAREST
        )
        cls.TEXTURE_ARROW = mcpython.util.texture.to_pyglet_image(texture_fire)
        cls.TEXTURE_ARROW_SIZE = texture_fire.size

    @classmethod
    def get_config_file(cls) -> str or None:
        return "assets/config/inventory/block_inventory_furnace.json"

    @classmethod
    def is_fuel(cls, itemstack):
        return not itemstack.is_empty() and hasattr(itemstack.item, "FUEL")

    def __init__(self, block, types: typing.List[str]):
        super().__init__()

        # todo: this should be at the container
        self.block = block
        self.fuel_left = 0.0
        self.fuel_max = 0.0
        self.xp_stored = 0.0
        self.smelt_start: typing.Optional[float] = None
        self.old_item_name = None
        self.recipe = None
        self.progress = 0.0
        self.types = types

        if self.custom_name is None:
            self.custom_name = "Furnace"

    async def create_slot_renderers(self) -> list:
        # 1 input, 1 fuel and 1 output
        slots = [
            mcpython.client.gui.Slot.Slot(
                on_update=self.on_input_update, on_shift_click=self.on_shift_click
            ),
            mcpython.client.gui.Slot.Slot(
                on_update=self.on_fuel_slot_update,
                on_shift_click=self.on_shift_click,
                allowed_item_test=self.is_fuel,
            ),
            mcpython.client.gui.Slot.Slot(
                on_update=self.on_output_update, on_shift_click=self.on_shift_click
            ),
        ]

        return slots

    # todo: this should be at the container
    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)
        buffer.write_float(self.fuel_left)
        buffer.write_float(self.fuel_max)
        buffer.write_float(self.xp_stored)
        buffer.write_float(
            time.time() - self.smelt_start if self.smelt_start else time.time()
        )
        buffer.write_float(self.progress)
        await buffer.write_list(self.types, buffer.write_string)

    # todo: this should be at the container
    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)
        self.fuel_left = buffer.read_float()
        self.fuel_max = buffer.read_float()
        self.xp_stored = buffer.read_float()
        self.smelt_start = buffer.read_float() + time.time()
        self.progress = buffer.read_float()
        self.types = await buffer.collect_list(buffer.read_string)

    # todo: this should be at the container
    def reset(self):
        self.block.active = False
        self.smelt_start = None
        self.recipe = None
        self.old_item_name = None
        if shared.IS_CLIENT:
            self.block.face_info.update(True)

    def update_status(self):
        if any(
            [
                self.slots[0].get_itemstack().get_item_name()
                in shared.crafting_handler.furnace_recipes[x]
                for x in self.types
                if x
                in shared.crafting_handler.furnace_recipes  # todo: why do we need this?
            ]
        ):
            if self.fuel_left == 0:
                if self.slots[1].get_itemstack().is_empty():
                    self.reset()
                    return
                # consume one fuel
                try:
                    fuel = self.slots[1].get_itemstack().item.FUEL
                    self.fuel_max = fuel
                    self.fuel_left += fuel
                except AttributeError:
                    logger.println(
                        "[FUEL][WARNING] item '{}' was marked as fuel but did NOT have FUEL-attribute".format(
                            self.slots[1].get_itemstack().get_item_name()
                        )
                    )
                    self.reset()
                    return
                self.slots[1].get_itemstack().add_amount(-1)

            if self.slots[0].get_itemstack().get_item_name() == self.old_item_name:
                return

            self.old_item_name = self.slots[0].get_itemstack().get_item_name()
            self.smelt_start = time.time()
            for x in self.types:
                if self.old_item_name in shared.crafting_handler.furnace_recipes[x]:
                    recipe = shared.crafting_handler.check_relink(
                        shared.crafting_handler.furnace_recipes[x][self.old_item_name]
                    )
                    break
            else:
                logger.println("[ERROR] no recipe found")
                self.reset()
                return

            if self.slots[2].get_itemstack().get_item_name() is not None and (
                self.slots[2].get_itemstack().get_item_name() != recipe.output
                or self.slots[2].get_itemstack().amount
                >= self.slots[2].get_itemstack().item.STACK_SIZE
            ):
                # if not self.slots[2].itemstack.is_empty():
                #     print(self.slots[2].itemstack.get_item_name() != recipe.output,
                #           self.slots[2].itemstack.amount, self.slots[2].itemstack.item.STACK_SIZE)
                self.reset()
                return
            self.recipe: mcpython.common.container.crafting.FurnaceCraftingHelper.FurnaceRecipe = (
                recipe
            )
            self.block.active = True
            if shared.IS_CLIENT:
                self.block.face_info.update()
        else:
            self.reset()

    @staticmethod
    async def on_shift_click(slot, x, y, button, mod, player):
        slot_copy = slot.itemstack.copy()

        if await shared.world.get_active_player().pick_up_item(slot_copy):
            slot.itemstack.clean()  # if we successfully added the itemstack, we have to clear it
        else:
            slot.itemstack.set_amount(slot_copy.itemstack.amount)

    def on_input_update(self, player=False):
        if self.slots[0].get_itemstack().is_empty():
            self.reset()
        else:
            self.update_status()

    def on_fuel_slot_update(self, player=False):
        self.update_status()

    def on_output_update(self, player=False):
        self.update_status()

    async def on_activate(self):
        await super().on_activate()
        try:
            mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "user:keyboard:press", self.on_key_press
            )
            mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "tickhandler:general", self.on_tick
            )
        except ValueError:
            pass

        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "tickhandler:general", self.on_tick
        )

    async def on_deactivate(self):
        await super().on_deactivate()
        await shared.world.get_active_player().reset_moving_slot()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "tickhandler:general", self.on_tick
        )

    def draw(self, hovering_slot=None):
        """
        Draws the inventory
        """
        self.bg_image_size = self.TEXTURE_BG_SIZE
        x, y = self.get_position()
        self.TEXTURE_BG.blit(x, y)

        # draw arrow
        if self.recipe and self.progress > 0:
            try:
                self.TEXTURE_ARROW.get_region(
                    0,
                    0,
                    round(self.TEXTURE_ARROW_SIZE[0] * self.progress),
                    self.TEXTURE_ARROW_SIZE[1],
                ).blit(x + 159, y + 229)
            except ZeroDivisionError:
                pass

        # draw fire
        if self.fuel_max > 0:
            try:
                self.TEXTURE_FIRE.get_region(
                    0,
                    0,
                    self.TEXTURE_FIRE_SIZE[0],
                    round(self.TEXTURE_FIRE_SIZE[1] * (self.fuel_left / self.fuel_max)),
                ).blit(x + 112, y + 229)
            except ZeroDivisionError:
                pass

        super().draw(hovering_slot)

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventory_main.slots[:36] + self.slots

    async def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            await shared.inventory_handler.hide(self)

    async def on_tick(self, dt):
        elapsed_time = time.time() - self.smelt_start if self.smelt_start else 0

        if self.fuel_left > 0:
            self.fuel_left = max(self.fuel_left - round(dt * 100) / 100, 0)
        elif self.progress and self.recipe:
            self.progress -= elapsed_time / self.recipe.time
            self.progress = max(self.progress, 0)

        if self.recipe is not None:
            if self.fuel_left == 0:
                if self.progress > 0.99:
                    await self.finish()
                else:
                    self.update_status()
                return

            self.progress = min(elapsed_time / self.recipe.time, 1)
            if self.progress >= 1:
                await self.finish()

        elif not self.slots[0].get_itemstack().is_empty() and (
            not self.slots[1].get_itemstack().is_empty() or self.fuel_left > 0
        ):
            self.update_status()

    async def finish(self):
        if self.slots[2].get_itemstack().is_empty():
            self.slots[2].set_itemstack(
                mcpython.common.container.ResourceStack.ItemStack(self.recipe.output)
            )
        else:
            if (
                self.slots[2].get_itemstack().item.STACK_SIZE
                > self.slots[2].get_itemstack().amount
            ):
                self.slots[2].get_itemstack().add_amount(1)

        self.slots[0].get_itemstack().add_amount(-1)
        try:
            await (await shared.world.get_active_player_async()).add_xp(self.recipe.xp)
        except AttributeError:
            pass

        self.smelt_start = time.time()
        self.update_status()

    def load(self, data: dict) -> bool:
        if not isinstance(data, dict):
            logger.println("[FURNACE][FATAL]: invalid data loaded from saves: ", data)
            return False

        self.fuel_left = data.setdefault("fuel", 0)
        self.fuel_max = data.setdefault("max fuel", 0)
        self.xp_stored = data.setdefault("xp", 0)
        self.progress = data.setdefault("progress", 0)
        self.update_status()
        return True

    def save(self):
        return {
            "fuel": self.fuel_left,
            "max fuel": self.fuel_max,
            "xp": self.xp_stored,
            "progress": self.progress,
        }


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", InventoryFurnaceRenderer.update_texture
)
