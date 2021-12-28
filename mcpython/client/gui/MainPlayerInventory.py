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
import asyncio
import typing

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.InventoryCreativeTab
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.ResourceStack
import mcpython.common.item.AbstractArmorItem
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
from mcpython import shared
from mcpython.common.container.crafting.CraftingGridHelperInterface import (
    CraftingGridHelperInterface,
)


class MainPlayerInventory(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    inventory class for the main part of the inventory
    """

    TEXTURE = None
    TEXTURE_SIZE = None
    INSTANCES: typing.List["MainPlayerInventory"] = []

    @classmethod
    def create(cls, hotbar):
        if len(cls.INSTANCES) > 0:
            instance = cls.INSTANCES.pop()
            instance.hotbar = hotbar
            return instance
        return cls(hotbar)

    @classmethod
    async def update_texture(cls):
        texture = await mcpython.engine.ResourceLoader.read_image(
            "minecraft:gui/container/inventory"
        )
        size = texture.size
        texture = texture.crop((0, 0, 176 / 255 * size[0], 164 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        ground = PIL.Image.new("RGBA", (texture.size[0], texture.size[1] + 4))
        ground.paste(texture)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(ground)
        cls.TEXTURE_SIZE = ground.size

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/player_inventory_main.json"

    def __init__(self, hotbar):
        self.hotbar = hotbar
        super().__init__()
        self.recipe_interface = None
        if self.custom_name is None:
            self.custom_name = "Inventory"

    # todo: move to container
    async def create_slot_renderers(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        slots = (
            [self.hotbar.slots[i].copy() for i in range(9)]
            + [mcpython.client.gui.Slot.Slot() for _ in range(27)]
            + [
                mcpython.client.gui.Slot.Slot(
                    allow_player_add_to_free_place=False, on_update=self.armor_update
                )
                for _ in range(4)
            ]
            + [
                mcpython.client.gui.Slot.Slot(allow_player_add_to_free_place=False)
                for _ in range(5)
            ]
            + [mcpython.client.gui.Slot.Slot()]
        )

        inputs = [slots[40:42], slots[42:44]]
        output = slots[44]
        self.recipe_interface = CraftingGridHelperInterface(inputs, output)

        return slots

    # todo: move to container
    def armor_update(self, player=None):
        # todo: add toughness
        # todo: move to player
        points = 0
        for slot in self.slots[35:40]:
            if slot.get_itemstack().item:
                if issubclass(
                    type(slot.get_itemstack().item),
                    mcpython.common.item.AbstractArmorItem.AbstractArmorItem,
                ):
                    points += slot.get_itemstack().item.DEFENSE_POINTS

        # todo: store somewhere the assigned player!
        if shared.IS_CLIENT:
            shared.world.get_active_player().armor_level = points

    def draw(self, hovering_slot=None):
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        super().draw(hovering_slot)

    async def remove_items_from_crafting(self):
        for slot in self.slots[40:-2]:
            slot: mcpython.client.gui.Slot.Slot
            itemstack = slot.get_itemstack()
            slot.set_itemstack(
                mcpython.common.container.ResourceStack.ItemStack.create_empty()
            )
            if not await shared.world.get_active_player().pick_up_item(itemstack):
                shared.world.get_active_dimension().spawn_itemstack_in_world(
                    itemstack, self.position
                )

        self.slots[-2].get_itemstack().clean()

    async def on_activate(self):
        if shared.world.get_active_player().gamemode == 1:
            await shared.inventory_handler.hide(self)
            await mcpython.client.gui.InventoryCreativeTab.CT_MANAGER.open()
        else:
            shared.tick_handler.schedule_once(self.reload_config())

    async def on_deactivate(self):
        await self.remove_items_from_crafting()
        shared.state_handler.active_state.parts[0].activate_mouse = True

    def update_shift_container(self):
        shared.inventory_handler.shift_container_handler.container_A = (
            self.slots[:9] + self.slots[36:41]
        )
        shared.inventory_handler.shift_container_handler.container_B = self.slots[9:36]

    def free(self):
        MainPlayerInventory.INSTANCES.append(self)


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", MainPlayerInventory.update_texture
)
