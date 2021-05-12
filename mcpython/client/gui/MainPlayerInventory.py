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

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.InventoryCreativeTab
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.ResourceStack
import mcpython.common.event.EventHandler
import mcpython.common.item.AbstractArmorItem
import mcpython.ResourceLoader
import mcpython.util.texture
import PIL.Image
from mcpython import shared


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
    def update_texture(cls):
        texture = mcpython.ResourceLoader.read_image(
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
        inputs = [self.slots[40:42], self.slots[42:44]]
        self.recipe_interface = mcpython.common.container.crafting.CraftingGridHelperInterface.CraftingGridHelperInterface(
            inputs, self.slots[44]
        )
        if self.custom_name is None:
            self.custom_name = "Inventory"

    # todo: move to container
    def create_slot_renderers(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        return (
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
        shared.world.get_active_player().armor_level = points

    def draw(self, hovering_slot=None):
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        super().draw(hovering_slot)

    def remove_items_from_crafting(self):
        for slot in self.slots[40:-2]:
            slot: mcpython.client.gui.Slot.Slot
            itemstack = slot.get_itemstack()
            slot.set_itemstack(
                mcpython.common.container.ResourceStack.ItemStack.create_empty()
            )
            if not shared.world.get_active_player().pick_up_item(itemstack):
                pass  # todo: drop item as item could not be added to inventory
        self.slots[-2].get_itemstack().clean()

    def on_activate(self):
        if shared.world.get_active_player().gamemode == 1:
            shared.inventory_handler.hide(self)
            mcpython.client.gui.InventoryCreativeTab.CT_MANAGER.open()

    def on_deactivate(self):
        self.remove_items_from_crafting()
        shared.state_handler.active_state.parts[0].activate_mouse = True

    def update_shift_container(self):
        shared.inventory_handler.shift_container.container_A = (
            self.slots[:9] + self.slots[36:41]
        )
        shared.inventory_handler.shift_container.container_B = self.slots[9:36]

    def free(self):
        MainPlayerInventory.INSTANCES.append(self)


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", MainPlayerInventory.update_texture
)
