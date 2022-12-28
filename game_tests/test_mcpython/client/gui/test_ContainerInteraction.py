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
from unittest import skipUnless

from pyglet.canvas.xlib import NoSuchDisplayException

from game_tests.util import TestCase

try:
    import pyglet.window

    HAS_VISUAL = True
except (ImportError, NoSuchDisplayException):
    HAS_VISUAL = False
else:
    from mcpython import shared

    shared.IS_TEST_ENV = True
    shared.IS_CLIENT = False

    import bytecodemanipulation.MutableFunction
    from mcpython.client.gui.ContainerRenderer import ContainerRenderer
    from mcpython.client.gui.ContainerRenderingManager import OpenedInventoryStatePart
    from mcpython.client.gui.Slot import ISlot, Slot
    from mcpython.common.container.ResourceStack import ItemStack
    from mcpython.common.factory.ItemFactory import ItemFactory
    from pyglet.window import key, mouse

    test_item = ItemFactory().set_name("minecraft:test_item").finish()
    test_item_2 = ItemFactory().set_name("minecraft:test_item_2").finish()

    class FakeWindow:
        mouse_position = 0, 0

        @classmethod
        def get_size(cls):
            return 100, 100

    class Inventory(ContainerRenderer):
        def add_slot(self, slot: Slot):
            self.slots.append(slot)
            return self


@skipUnless(HAS_VISUAL, "rendering backend is needed")
class ContainerInteraction(TestCase):
    def setUp(self) -> None:
        shared.IS_CLIENT = True

        self.interaction_manager = OpenedInventoryStatePart()
        shared.window = FakeWindow

    def tearDown(self) -> None:
        shared.window = None

    async def test_key_forward(self):
        inventory = Inventory()

        invoked = False

        def test(x, y, button, modifiers):
            nonlocal invoked

            invoked = True

            self.assertEqual(button, 10)
            self.assertEqual(modifiers, 20)
            self.assertEqual(x, 2)
            self.assertEqual(y, 6)

        shared.IS_CLIENT = False
        s = Slot()
        inventory.add_slot(s)
        s.on_button_press = test

        await shared.inventory_handler.add(inventory)
        await shared.inventory_handler.show(inventory)

        shared.window.mouse_position = 52, 56

        await self.interaction_manager.on_key_press(10, 20)
        self.assertTrue(invoked)

    async def test_key_forward_not_hit(self):
        inventory = Inventory()

        invoked = False

        def test(x, y, button, modifiers):
            nonlocal invoked

            invoked = True

        shared.IS_CLIENT = False
        s = Slot()
        inventory.add_slot(s)
        s.on_button_press = test

        await shared.inventory_handler.add(inventory)
        await shared.inventory_handler.show(inventory)

        shared.window.mouse_position = 20, 20

        await self.interaction_manager.on_key_press(10, 20)
        self.assertFalse(invoked)

    async def test_left_pickup(self):
        inventory = Inventory()

        shared.IS_CLIENT = False
        s = Slot()
        s.set_itemstack(ItemStack(test_item(), 8))
        inventory.add_slot(s)

        await shared.inventory_handler.add(inventory)
        await shared.inventory_handler.show(inventory)

        shared.window.mouse_position = 50, 50

        self.interaction_manager.moving_itemstack = (
            shared.inventory_handler.moving_slot.itemstack.copy()
        )
        await self.interaction_manager.handle_left_click(
            mouse.LEFT, 0, shared.inventory_handler.moving_slot.itemstack, s, 50, 50
        )
        self.assertEqual(shared.inventory_handler.moving_slot.itemstack.amount, 8)
        self.assertEqual(
            shared.inventory_handler.moving_slot.itemstack.get_item_name(),
            "minecraft:test_item",
        )
        self.assertEqual(s.get_itemstack().get_item_name(), None)
        shared.inventory_handler.moving_slot.itemstack.clean()

    async def test_left_exchange(self):
        inventory = Inventory()

        shared.IS_CLIENT = False
        s = Slot()
        s.set_itemstack(ItemStack(test_item(), 8))
        inventory.add_slot(s)

        await shared.inventory_handler.add(inventory)
        await shared.inventory_handler.show(inventory)

        shared.window.mouse_position = 50, 50

        shared.inventory_handler.moving_slot.set_itemstack(ItemStack(test_item_2(), 5))

        self.interaction_manager.moving_itemstack = (
            shared.inventory_handler.moving_slot.itemstack.copy()
        )
        await self.interaction_manager.handle_left_click(
            mouse.LEFT, 0, shared.inventory_handler.moving_slot.itemstack, s, 50, 50
        )
        self.assertEqual(shared.inventory_handler.moving_slot.itemstack.amount, 8)
        self.assertEqual(
            shared.inventory_handler.moving_slot.itemstack.get_item_name(),
            "minecraft:test_item",
        )
        self.assertEqual(s.get_itemstack().get_item_name(), "minecraft:test_item_2")
        self.assertEqual(s.get_itemstack().amount, 5)
        shared.inventory_handler.moving_slot.itemstack.clean()

    async def test_right_pickup_half(self):
        inventory = Inventory()

        shared.IS_CLIENT = False
        s = Slot()
        s.set_itemstack(ItemStack(test_item(), 4))
        inventory.add_slot(s)

        await shared.inventory_handler.add(inventory)
        await shared.inventory_handler.show(inventory)

        shared.window.mouse_position = 50, 50

        self.interaction_manager.moving_itemstack = (
            shared.inventory_handler.moving_slot.itemstack.copy()
        )
        await self.interaction_manager.handle_right_click(
            mouse.RIGHT, 0, shared.inventory_handler.moving_slot.itemstack, s, 50, 50
        )
        self.assertEqual(
            shared.inventory_handler.moving_slot.itemstack.get_item_name(),
            "minecraft:test_item",
        )
        self.assertEqual(shared.inventory_handler.moving_slot.itemstack.amount, 2)
        self.assertEqual(s.get_itemstack().get_item_name(), "minecraft:test_item")
        self.assertEqual(s.get_itemstack().amount, 2)
        shared.inventory_handler.moving_slot.itemstack.clean()
