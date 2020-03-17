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
import entity.Entity
import rendering.EntityRenderer


@globals.registry
class Player(entity.Entity.Entity):
    RENDERER = rendering.EntityRenderer.EntityRenderer("minecraft:player")

    NAME = "minecraft:player"

    GAMEMODE_DICT: dict = {
        "survival": 0, "0": 0,
        "creative": 1, "1": 1,
        "adventure": 2, "2": 2,
        "spectator": 3, "3": 3
    }

    def __init__(self, name, dimension=None):
        super().__init__(dimension=dimension)
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

        self.inventories: dict = {}

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
        clipboard.copy("/tp @p {} {} {}".format(*self.position))

    def toggle_gamemode(self):
        if self.gamemode == 1: self.set_gamemode(3)
        elif self.gamemode == 3: self.set_gamemode(1)

    def create_inventories(self):
        import gui.InventoryPlayerHotbar
        import gui.InventoryPlayerMain
        import gui.InventoryChest
        import gui.InventoryCraftingTable

        hotbar = self.inventories['hotbar'] = gui.InventoryPlayerHotbar.InventoryPlayerHotbar()
        self.inventories['main'] = gui.InventoryPlayerMain.InventoryPlayerMain(hotbar)
        self.inventories['chat'] = chat.Chat.ChatInventory()
        self.inventories["enderchest"] = gui.InventoryChest.InventoryChest()
        self.inventories["crafting_table"] = gui.InventoryCraftingTable.InventoryCraftingTable()

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

    def pick_up(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        # have we an slot?
        if type(itemstack) in (gui.Slot.Slot, gui.Slot.SlotCopy): itemstack = itemstack.get_itemstack()
        if type(itemstack) == list:
            return all([self.pick_up(itemstack) for itemstack in itemstack])

        if not itemstack.item or itemstack.amount == 0:
            return True
        for inventory_name, reverse in self.inventory_order:
            inventory = self.inventories[inventory_name]
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
            inventory = self.inventories[inventory_name]
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
        return self.inventories["hotbar"].slots[self.active_inventory_slot]

    def kill(self, test_totem=True):
        if test_totem:
            # todo: add effects
            if self.get_active_inventory_slot().get_itemstack().get_item_name() == "minecraft:totem_of_undying":
                self.get_active_inventory_slot().get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
            elif self.inventories["main"].slots[45].get_itemstack().get_item_name() == "minecraft:totem_of_undying":
                self.inventories["main"].slots[45].get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
        super().kill()  # todo: create an new entity for player
        sector = util.math.sectorize(self.position)
        globals.world.change_sectors(sector, None)
        if not globals.world.gamerulehandler.table["keepInventory"].status.status:
            globals.commandparser.parse("/clear")
        if globals.world.gamerulehandler.table["showDeathMessages"].status.status:
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
        sector = util.math.sectorize(self.position)
        globals.world.change_sectors(None, sector)
        # todo: recalculate armor level!

        if not globals.world.gamerulehandler.table["doImmediateRespawn"].status.status:
            globals.statehandler.switch_to("minecraft:escape_state")  # todo: add special state

    def _get_position(self):
        return self.position

    def _set_position(self, position):
        self.position = position

    def damage(self, hearts: int, check_gamemode=True, reason=None):
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
        self.pick_up(globals.inventoryhandler.moving_slot.get_itemstack().copy())
        globals.inventoryhandler.moving_slot.get_itemstack().clean()

    def tell(self, msg: str):
        globals.chat.print_ln(msg)

    def draw(self):
        rx, ry, rz = self.rotation
        rotation_whole = (0, rx+90, 0)
        rra = (0, 0, 0) if self.get_active_inventory_slot().itemstack.is_empty() else (45, 0, 0)
        rla = (0, 0, 0) if self.inventories["main"].slots[-1].itemstack.is_empty() else (45, 0, 0)
        self.RENDERER.draw(self, "inner" if self == globals.world.get_active_player() else "outer",
                           part_rotation={"head": (0, 0, 0), "right_arm": rra, "left_arm": rla},
                           rotation=rotation_whole)
