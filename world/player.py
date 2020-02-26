"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals
import gui.ItemStack
import gui.Slot
import chat.Chat
import util.math
import ResourceLocator
import mod.ModMcpython
import logger
import event.EventHandler


class Player:
    GAMEMODE_DICT: dict = {
        "survival": 0, "0": 0,
        "creative": 1, "1": 1,
        "adventure": 2, "2": 2,
        "spectator": 3, "3": 3
    }

    def __init__(self, name):
        globals.player = self

        self.name: str = name
        self.gamemode: int = -1
        self.set_gamemode(1)
        self.hearts: int = 20
        self.hunger: int = 20
        self.xp: int = 0
        self.xp_level: int = 0
        self.armor_level = 0
        self.armor_toughness = 0

        self.fallen_since_y = -1 

        self.inventorys: dict = {}

        self.inventory_order: list = [  # an ([inventoryindexname: str], [reversed slots: bool}) list
            ("hotbar", False),
            ("main", False)
        ]

        self.active_inventory_slot: int = 0

        self.iconparts = []

        mod.ModMcpython.mcpython.eventbus.subscribe("stage:inventories", self.create_inventories,
                                                    info="setting up player inventory")
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:get_player_position", self.hotkey_get_position)
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:gamemode_1-3_toggle", self.toggle_gamemode)

    def hotkey_get_position(self):
        import clipboard
        clipboard.copy("/tp @p {} {} {}".format(*globals.window.position))

    def toggle_gamemode(self):
        if self.gamemode == 1: self.set_gamemode(3)
        elif self.gamemode == 3: self.set_gamemode(1)

    def create_inventories(self):
        import gui.InventoryPlayerHotbar
        import gui.InventoryPlayerMain
        import gui.InventoryChest

        hotbar = self.inventorys['hotbar'] = gui.InventoryPlayerHotbar.InventoryPlayerHotbar()
        self.inventorys['main'] = gui.InventoryPlayerMain.InventoryPlayerMain(hotbar)
        self.inventorys['chat'] = chat.Chat.ChatInventory()
        self.inventorys["enderchest"] = gui.InventoryChest.InventoryChest()

        self.iconparts = [(ResourceLocator.read("build/texture/gui/icons/hart.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hart_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hart_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/hunger.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hunger_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hunger_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/armor.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/armor_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/armor_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/xp_bar_empty.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/xp_bar.png", "pyglet"))]

        import block.BlockCraftingTable, gui.InventoryCraftingTable
        block.BlockCraftingTable.BlockCraftingTable.inventory = gui.InventoryCraftingTable.InventoryCraftingTable()

    def set_gamemode(self, gamemode: int or str):
        gamemode = self.GAMEMODE_DICT.get(gamemode, gamemode)
        # if it is a repr of the gamemode, get the int gamemode
        # else, return the int
        if gamemode == 0:
            globals.window.flying = False
        elif gamemode == 1:
            pass
        elif gamemode == 2:
            globals.window.flying = False
        elif gamemode == 3:
            globals.window.flying = True
        else:
            raise ValueError("can't cast {} to valid gamemode".format(gamemode))
        self.gamemode = gamemode

    def get_needed_xp_for_next_level(self) -> int:
        if self.xp_level < 16:
            return self.xp_level * 2 + 5
        elif self.xp_level < 30:
            return 37 + (self.xp_level - 15) * 5
        else:
            return 107 + (self.xp_level - 29) * 9

    def add_xp(self, xp: int):
        while xp > 0:
            if self.xp + xp < self.get_needed_xp_for_next_level():
                self.xp += xp
                return
            elif xp > self.get_needed_xp_for_next_level():
                xp -= self.get_needed_xp_for_next_level()
                self.xp_level += 1
            else:
                xp = xp - (self.get_needed_xp_for_next_level() - self.xp)
                self.xp_level += 1

    def add_xp_level(self, xp_levels: int):
        self.xp_level += xp_levels

    def add_to_free_place(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        # have we an slot?
        if type(itemstack) == gui.Slot.Slot: itemstack = itemstack.get_itemstack()

        if not itemstack.item or itemstack.amount == 0:
            return True
        for inventory_name, reverse in self.inventory_order:
            inventory = self.inventorys[inventory_name]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if not slot.get_itemstack().is_empty() and slot.get_itemstack().get_item_name() == itemstack.get_item_name() and \
                        slot.interaction_mode[2]:
                    if slot.get_itemstack().item and slot.get_itemstack().amount + itemstack.amount <= itemstack.item. \
                            get_max_stack_size():
                        slot.get_itemstack().add_amount(itemstack.amount)
                        return True
                    else:
                        m = slot.get_itemstack().item.get_max_stack_size()
                        delta = m - slot.get_itemstack().amount
                        slot.get_itemstack().set_amount(m)
                        itemstack.add_amount(-delta)
                if itemstack.amount <= 0:
                    return True
        for inventory_name, reverse in self.inventory_order:
            inventory = self.inventorys[inventory_name]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if not slot.get_itemstack().item and slot.interaction_mode[2]:
                    slot.set_itemstack(itemstack)
                    return True
        return False

    def set_active_inventory_slot(self, slot: int):
        self.active_inventory_slot = slot

    def get_active_inventory_slot(self):
        return self.inventorys["hotbar"].slots[self.active_inventory_slot]

    def kill(self, test_totem=True):
        if test_totem:
            # todo: add effects
            if self.get_active_inventory_slot().get_itemstack().get_item_name() == "minecraft:totem_of_undying":
                self.get_active_inventory_slot().get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
            elif self.inventorys["main"].slots[45].get_itemstack().get_item_name() == "minecraft:totem_of_undying":
                self.inventorys["main"].slots[45].get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
        globals.commandparser.parse("/clear")
        logger.println("[CHAT] player {} died".format(self.name))
        self.position = (globals.world.spawnpoint[0], util.math.get_max_y(globals.world.spawnpoint),
                         globals.world.spawnpoint[1])
        self.active_inventory_slot = 0
        globals.window.dy = 0
        globals.chat.close()
        self.xp = 0
        self.xp_level = 0
        self.hearts = 20
        self.hunger = 20
        globals.window.flying = False
        self.armor_level = 0
        self.armor_toughness = 0
        globals.eventhandler.call("player:die", self)
        self.reset_moving_slot()
        globals.inventoryhandler.close_all_inventories()
        # todo: recalculate armor level!

    def _get_position(self):
        return globals.window.position

    def _set_position(self, position):
        globals.window.position = position

    position = property(_get_position, _set_position)

    def damage(self, hearts: int, check_gamemode=True):
        """
        damage the player and removes the given amount of hearts (two hearts are one full displayed hart)
        """
        hearts = hearts * (1 - min([20, max([self.armor_level / 5, self.armor_level -
                                             hearts / (2 + self.armor_toughness / 4)])]))
        if self.gamemode in [0, 2] or not check_gamemode:
            self.hearts -= hearts
            if self.hearts <= 0:
                self.kill()

    def reset_moving_slot(self):
        self.add_to_free_place(globals.inventoryhandler.moving_slot.get_itemstack().copy())
        globals.inventoryhandler.moving_slot.get_itemstack().clean()
