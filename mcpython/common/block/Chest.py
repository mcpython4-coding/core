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
from datetime import datetime

import mcpython.engine.physics.AxisAlignedBoundingBox
import mcpython.util.enums
import pyglet
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from pyglet.window import key, mouse

from .IBlockContainerExposer import SimpleInventoryWrappingContainer
from .IHorizontalOrientableBlock import IHorizontalOrientableBlock

if shared.IS_CLIENT:
    from mcpython.client.rendering.blocks.ChestRenderer import IChestRendererSupport, ChestRenderer
else:
    class IChestRendererSupport:
        pass

# the bounding box of the chest
BBOX = mcpython.engine.physics.AxisAlignedBoundingBox.AxisAlignedBoundingBox(
    (14 / 16, 14 / 16, 14 / 16), (1 / 16, 1 / 16, 1 / 16)
)


class Chest(
    IHorizontalOrientableBlock,
    IChestRendererSupport,
    SimpleInventoryWrappingContainer,
):
    """
    The Chest block class
    """

    # now, for deciding to render the Christmas variant or not
    now: datetime = datetime.now()

    # If Christmas is today, or not
    IS_CHRISTMAS: bool = 24 <= now.day <= 26 and now.month == 12

    del now

    NAME: str = "minecraft:chest"
    MODEL_FACE_NAME = "side"

    HARDNESS = BLAST_RESISTANCE = 2.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.AXE}

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    if shared.IS_CLIENT:
        CHEST_BLOCK_RENDERER = None
        CHEST_BLOCK_RENDERER_CHRISTMAS = None

        @classmethod
        async def reload(cls):
            cls.CHEST_BLOCK_RENDERER = (
                mcpython.client.rendering.blocks.ChestRenderer.ChestRenderer(
                    "minecraft:entity/chest/normal"
                )
            )
            cls.CHEST_BLOCK_RENDERER_CHRISTMAS = (
                mcpython.client.rendering.blocks.ChestRenderer.ChestRenderer(
                    "minecraft:entity/chest/christmas"
                )
            )

        # As this can be statically decided, we use this trick for some performance gain
        if IS_CHRISTMAS:

            async def on_block_added(self):
                self.face_info.custom_renderer = self.CHEST_BLOCK_RENDERER_CHRISTMAS
                self.face_info.update(True)
                await self.inventory.init()
                await self.inventory.reload_config()

        else:

            async def on_block_added(self):
                self.face_info.custom_renderer = self.CHEST_BLOCK_RENDERER
                self.face_info.update(True)
                await self.inventory.init()
                await self.inventory.reload_config()

    def __init__(self):
        """
        Creates a new BlockChest block
        """
        super().__init__()

        import mcpython.client.gui.InventoryChest as InventoryChest

        self.inventory = InventoryChest.InventoryChest(self)
        self.loot_table_link = None

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)
        await self.inventory.write_to_network_buffer(buffer)

        buffer.write_string(
            self.loot_table_link if self.loot_table_link is not None else ""
        )

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)
        await self.inventory.read_from_network_buffer(buffer)

        self.loot_table_link = buffer.read_string()
        if self.loot_table_link == "":
            self.loot_table_link = None

    def can_open_inventory(self) -> bool:
        """
        Checks if the inventory can be opened
        :return: if the block can be opened
        """
        if self.position is None or self.dimension is None:
            return True

        x, y, z = self.position
        instance = shared.world.get_dimension_by_name(self.dimension).get_block(
            (x, y + 1, z)
        )
        return instance is None or not instance.face_solid & 2

    async def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
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

            await shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    async def get_all_inventories(self) -> tuple:
        return (self.inventory,)

    def get_view_bbox(self):
        return BBOX

    @classmethod
    def set_block_data(cls, instance, block):
        if hasattr(instance, "inventory"):
            block.inventory = instance.inventory.copy()

    async def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[pyglet.window.key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[pyglet.window.mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()

    async def on_block_remove(self, reason):
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            dimension = shared.world.get_dimension_by_name(self.dimension)

            for slot in self.inventory.slots:
                if slot.get_itemstack().is_empty():
                    continue

                dimension.spawn_itemstack_in_world(
                    slot.get_itemstack().copy(), self.position, pickup_delay=4
                )
                slot.get_itemstack().clean()

        await shared.inventory_handler.hide(self.inventory)
        del self.inventory

    @classmethod
    def modify_block_item(cls, factory):
        factory.set_fuel_level(15)


class TrappedChest(Chest):
    NAME = "minecraft:trapped_chest"

    # todo: add custom renderer
    # todo: add redstone control


if shared.IS_CLIENT:
    shared.tick_handler.schedule_once(Chest.reload())
    shared.tick_handler.schedule_once(TrappedChest.reload())
