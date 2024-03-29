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
from game_tests.test_mcpython.mockups import WorldMockup
from game_tests.util import TestCase
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer

shared.IS_TEST_ENV = True

import mcpython.common.item.ItemManager
from mcpython.common.factory.ItemFactory import ItemFactory

shared.IS_TEST_ENV = True


class FakeMod:
    class eventbus:
        @classmethod
        def subscribe(cls, *_, **__):
            pass


class FakeModloader:
    def __init__(self):
        self.finished = False

    def add_to_add(self, mod):
        pass

    def __call__(self, *args, **kwargs):
        return lambda func: None

    def __getitem__(self, item):
        return FakeMod


ItemFactory().set_name("fake:item").finish()


class TestPlayerEntity(TestCase):
    def setUp(self) -> None:
        from mcpython import shared

        shared.world = WorldMockup()

    def tearDown(self) -> None:
        from mcpython import shared

        shared.world = None

    def test_module_import(self):
        import mcpython.common.entity.PlayerEntity

    def test_constructor(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        self.assertEqual(instance.name, "test_player")

    def test_set_gamemode(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        instance.set_gamemode(1)

        self.assertEqual(instance.gamemode, 1)

        instance.set_gamemode("survival")

        self.assertEqual(instance.gamemode, 0)

    async def test_set_active_inventory_slot(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")

        await instance.set_active_inventory_slot(3)
        self.assertEqual(instance.active_inventory_slot, 3)

        await instance.set_active_inventory_slot(-1)
        self.assertEqual(instance.active_inventory_slot, 0)

        await instance.set_active_inventory_slot(100)
        self.assertEqual(instance.active_inventory_slot, 8)

    def test_on_inventory_cleared(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")
        instance.xp = 0
        instance.xp_level = 0

        instance.on_inventory_cleared()

        self.assertEqual(instance.xp, 0)
        self.assertEqual(instance.xp_level, 0)

    # Test for issue 1000
    async def test_pickup_item(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity
        from mcpython.client.gui.Slot import SlotCopy
        from mcpython.common.container.ResourceStack import ItemStack

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")
        await instance.create_inventories()
        await instance.pick_up_item(ItemStack("fake:item", 32))

        count = 0

        for inventory in instance.inventory_order:
            for slot in inventory[0].slots:
                if (
                    not isinstance(slot, SlotCopy)
                    and slot.get_itemstack().get_item_name() == "fake:item"
                ):
                    count += slot.get_itemstack().amount

        self.assertEqual(count, 32)

    async def test_serializer(self):
        import mcpython.common.container.crafting.CraftingManager
        import mcpython.common.entity.PlayerEntity

        shared.IS_CLIENT = False

        shared.mod_loader = FakeModloader()

        instance = mcpython.common.entity.PlayerEntity.PlayerEntity(name="test_player")
        instance.set_gamemode(0)
        await instance.create_inventories()

        # This simulates fall damage
        instance.damage(2.3)

        buffer = WriteBuffer()
        await instance.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        new_instance = mcpython.common.entity.PlayerEntity.PlayerEntity()
        await new_instance.read_from_network_buffer(read_buffer)

        self.assertEqual(instance.name, new_instance.name)
        self.assertEqual(instance.dimension, new_instance.dimension)
        self.assertEqual(instance.hearts, new_instance.hearts)
        self.assertNotEqual(instance.hearts, 20)
        self.assertEqual(new_instance.gamemode, 0)
