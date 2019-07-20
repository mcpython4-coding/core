"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import gui.InventoryPlayerHotbar
import gui.InventoryPlayerMain
import gui.ItemStack
import gui.Slot
import chat.Chat


class Player:
    GAMEMODE_DICT: dict = {
        "survival": 0, "0": 0,
        "creative": 1, "1": 1,
        "adventure": 2, "2": 2,
        "spectator": 3, "3": 3
    }

    def __init__(self, name):
        G.player: Player = self

        self.name: str = name
        self.gamemode: int = -1
        self.set_gamemode(1)
        self.harts: int = 20
        self.hunger: int = 20
        self.xp: int = 0
        self.xp_level: int = 0

        self.inventorys: dict = {}

        self.inventorys["hotbar"] = gui.InventoryPlayerHotbar.InventoryPlayerHotbar()
        self.inventorys["main"] = gui.InventoryPlayerMain.InventoryPlayerMain()
        self.inventorys["chat"] = chat.Chat.ChatInventory()

        self.inventory_order: list = [  # an ([inventoryindexname], [reversed slots}) list
            ("hotbar", False),
            ("main", True)
        ]

        self.active_inventory_slot: int = 0

    def set_gamemode(self, gamemode: int or str):
        if gamemode in self.GAMEMODE_DICT:
            gamemode = self.GAMEMODE_DICT[gamemode]
        self.gamemode = gamemode
        if gamemode == 0:
            G.window.flying = False
        elif gamemode == 1:
            pass
        elif gamemode == 2:
            G.window.flying = False
        elif gamemode == 3:
            G.window.flying = True
        else:
            raise ValueError("can't cast {} to valid gamemode".format(gamemode))

    def _get_needed_xp_for_next_level(self) -> int:
        if self.xp_level < 16:
            return self.xp_level * 2 + 5
        elif self.xp_level < 30:
            return 37 + (self.xp_level - 15) * 5
        else:
            return 107 + (self.xp_level - 29) * 9

    def add_xp(self, xp: int):
        while xp > 0:
            if self.xp + xp < self._get_needed_xp_for_next_level():
                self.xp += xp
                return
            elif xp > self._get_needed_xp_for_next_level():
                xp -= self._get_needed_xp_for_next_level()
                self.xp_level += 1
            else:
                xp = xp - (self._get_needed_xp_for_next_level() - self.xp)
                self.xp_level += 1

    def add_xp_level(self, xp_levels: int):
        self.xp_level += 1

    def add_to_free_place(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        if not itemstack.item or itemstack.amount == 0: return True
        for inventoryname, reverse in self.inventory_order:
            inventory = self.inventorys[inventoryname]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if slot.itemstack.item and slot.itemstack.item.get_name() == itemstack.item.get_name() and \
                        slot.interaction_mode[2]:
                    if slot.itemstack.item and slot.itemstack.amount + itemstack.amount <= itemstack.item.\
                            get_max_stack_size():
                        slot.itemstack.amount += itemstack.amount
                        return True
                    else:
                        m = slot.itemstack.item.get_max_stack_size()
                        delta = m - slot.itemstack.amount
                        slot.itemstack.amount = m
                        itemstack.amount -= delta
                if itemstack.amount <= 0:
                    return True
        for inventoryname, reverse in self.inventory_order:
            inventory = self.inventorys[inventoryname]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if not slot.itemstack.item and slot.interaction_mode[2]:
                    slot.itemstack = itemstack
                    return True
        return False

    def set_active_inventory_slot(self, id: int):
        self.active_inventory_slot = id

    def get_active_inventory_slot(self):
        return self.inventorys["hotbar"].slots[self.active_inventory_slot]

