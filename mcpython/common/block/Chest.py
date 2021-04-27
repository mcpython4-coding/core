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
from datetime import datetime

import pyglet
from pyglet.window import mouse, key

import mcpython.common.block.BoundingBox
from mcpython import shared, logger
import mcpython.common.item.AbstractToolItem
import mcpython.util.enums
from . import AbstractBlock
import mcpython.client.rendering.blocks.TemporaryChestRenderer
import mcpython.common.block.PossibleBlockStateBuilder

BBOX = mcpython.common.block.BoundingBox.BoundingBox(
    (14 / 16, 14 / 16, 14 / 16), (1 / 16, 1 / 16, 1 / 16)
)  # the bounding box of the chest


class Chest(AbstractBlock.AbstractBlock):
    """
    The Chest block class
    """

    now: datetime = datetime.now()  # now
    is_christmas: bool = (
        24 <= now.day <= 26 and now.month == 12
    )  # if christmas is today

    NAME: str = "minecraft:chest"  # the name of the chest

    IS_SOLID = False

    HARDNESS = 2.5
    BLAST_RESISTANCE = 2.5

    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.AXE]

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_side_horizontal("side")
        .build()
    )

    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )

    def __init__(self):
        """
        Creates a new BlockChest block
        """
        super().__init__()

        self.front_side = mcpython.util.enums.EnumSide.N
        import mcpython.client.gui.InventoryChest as InventoryChest

        self.inventory = InventoryChest.InventoryChest()
        self.loot_table_link = None

    def on_block_added(self):
        if self.real_hit:
            dx, dz = (
                self.real_hit[0] - self.position[0],
                self.real_hit[1] - self.position[1],
            )
            if dx > 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.N
            elif dx < 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.S
            elif dz > 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.E
            elif dz < 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.W

        self.face_solid = {
            face: False for face in mcpython.util.enums.EnumSide.iterate()
        }
        self.face_state.custom_renderer = (
            mcpython.client.rendering.blocks.TemporaryChestRenderer.TemporaryChestRenderer()
        )
        if shared.IS_CLIENT:
            self.face_state.update(True)

    def can_open_inventory(self) -> bool:
        """
        Checks if the inventory can be opened
        :return: if the block can be opened
        """

        x, y, z = self.position
        instance = shared.world.get_dimension_by_name(self.dimension).get_block(
            (x, y + 1, z)
        )
        return (
            instance is None
            or not instance.face_solid[mcpython.util.enums.EnumSide.DOWN]
        )

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if (
            button == mouse.RIGHT
            and not modifiers & (key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL)
            and self.can_open_inventory()
        ):
            if self.loot_table_link:
                self.inventory.insert_items(
                    shared.loot_table_handler.roll(
                        self.loot_table_link, block=self, position=self.position
                    ),
                    random_check_order=True,
                    insert_when_same_item=False,
                )
                self.loot_table_link = None

            shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        return self.inventory.slots, self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]
            if type(face) == str:
                self.front_side = mcpython.util.enums.EnumSide[state["side"].upper()]
            else:
                self.front_side = face

    def get_model_state(self) -> dict:
        return {
            "side": self.front_side.normal_name,
        }

    def get_view_bbox(self):
        return BBOX

    @classmethod
    def set_block_data(cls, instance, block):
        if hasattr(instance, "inventory"):
            block.inventory = instance.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[pyglet.window.key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[pyglet.window.mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()

    def on_block_remove(self, reason):
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            for slot in self.inventory.slots:
                shared.world.get_active_player().pick_up_item(
                    slot.get_itemstack().copy()
                )
                slot.get_itemstack().clean()

        shared.inventory_handler.hide(self.inventory)
        del self.inventory

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(15)

    def get_save_data(self):
        return {"model": self.get_model_state(), "loot_table": self.loot_table_link}

    def load_data(self, data):
        if "model" in data:
            self.set_model_state(data["model"])
        else:
            logger.println(
                "[SERIALIZER][WARN] '{}' is missing model state in save files; this indicates a save error...".format(
                    self
                )
            )

        if "loot_table" in data:
            self.loot_table_link = data["loot_table"]
        else:
            logger.println(
                "[SERIALIZER][WARN] '{}' is missing loot table in save files; this indicates a save error...".format(
                    self
                )
            )