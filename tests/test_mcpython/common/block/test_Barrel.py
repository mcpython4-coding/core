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
from unittest import TestCase

from mcpython import shared
from pyglet.window import key, mouse
from test_mcpython.fakeHelpers import FakeCraftingHandler
from test_mcpython.fakeHelpers import FakeInventoryHandler
from test_mcpython.fakeHelpers import FakeWorld


class TestBarrel(TestCase):
    def test_module_import(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        self.assertEqual(mcpython.common.block.Barrel.Barrel.NAME, "minecraft:barrel")

    def test_on_block_added(self):
        shared.crafting_handler = FakeCraftingHandler()
        shared.world = FakeWorld

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler

        instance = mcpython.common.block.Barrel.Barrel()
        instance.position = 0, 0, 0
        instance.set_to = 0, -1, 0

        instance.on_block_added()

        self.assertEqual(instance.face.normal_name, "down")

        instance.set_to = 0, 0, 1

        instance.on_block_added()

        self.assertEqual(instance.face.normal_name, "south")

        shared.world = None

    async def test_on_player_interaction(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler
        FakeInventoryHandler.SHOWN = False

        instance = mcpython.common.block.Barrel.Barrel()

        await instance.on_player_interaction(None, mouse.RIGHT, 0, None, None)

        self.assertTrue(FakeInventoryHandler.SHOWN)

        FakeInventoryHandler.SHOWN = False

        await instance.on_player_interaction(None, mouse.RIGHT, key.MOD_SHIFT, None, None)

        self.assertFalse(FakeInventoryHandler.SHOWN)

    def test_model_state_serialization(self):
        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler

        instance = mcpython.common.block.Barrel.Barrel()
        state = instance.get_model_state()
        instance.set_model_state({"facing": "north", "open": "true"})
        self.assertNotEqual(state, instance.get_model_state())
        instance.set_model_state(state)
        self.assertEqual(state, instance.get_model_state())

    def test_serializer(self):
        from mcpython import shared
        from mcpython.common.container.ResourceStack import ItemStack
        from mcpython.common.item.AbstractItem import AbstractItem
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        shared.IS_CLIENT = False

        @shared.registry
        class TestItem(AbstractItem):
            NAME = "minecraft:test_item"

        shared.crafting_handler = FakeCraftingHandler()

        import mcpython.common.block.Barrel

        shared.inventory_handler = FakeInventoryHandler
        FakeInventoryHandler.SHOWN = False

        instance = mcpython.common.block.Barrel.Barrel()
        instance.inventory.slots[0].set_itemstack(ItemStack(TestItem()))

        buffer = WriteBuffer()
        instance.write_to_network_buffer(buffer)

        instance2 = mcpython.common.block.Barrel.Barrel()
        instance2.read_from_network_buffer(ReadBuffer(buffer.get_data()))

        self.assertEqual(
            instance2.inventory.slots[0].get_itemstack().get_item_name(),
            "minecraft:test_item",
        )
