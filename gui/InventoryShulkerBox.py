"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.InventoryChest
import item.IShulkerBoxLikeItem


class InventoryShulkerBox(gui.InventoryChest.InventoryChest):
    def create_slots(self) -> list:
        slots = super().create_slots()
        for slot in slots:
            slot.allowed_item_func = self.test_for_shulker
        return slots

    def test_for_shulker(self, itemstack):
        if itemstack.item and issubclass(type(itemstack.item), item.IShulkerBoxLikeItem.IShulkerBoxLikeItem):
            return not itemstack.item.is_blocked_in(self)
        return True

