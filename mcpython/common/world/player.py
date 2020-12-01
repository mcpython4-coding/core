"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals, globals as G, logger
import mcpython.ResourceLocator
import mcpython.client.chat.Chat
import mcpython.common.entity.Entity
import mcpython.common.event.EventHandler
import mcpython.client.gui.InventoryChest
import mcpython.client.gui.InventoryPlayerMain
import mcpython.client.gui.ItemStack
import mcpython.client.gui.Slot
import mcpython.common.mod.ModMcpython
import mcpython.client.rendering.EntityRenderer
import mcpython.util.math
import mcpython.common.entity.DamageSource


@G.registry
class Player(mcpython.common.entity.Entity.Entity):
    RENDERER = mcpython.client.rendering.EntityRenderer.EntityRenderer(
        "minecraft:player"
    )

    NAME = "minecraft:player"
    SUMMON_ABLE = False

    GAMEMODE_DICT: dict = {
        "survival": 0,
        "0": 0,
        "creative": 1,
        "1": 1,
        "adventure": 2,
        "2": 2,
        "spectator": 3,
        "3": 3,
    }

    def __init__(self, name="unknown", dimension=None):
        super().__init__(dimension=dimension)

        self.name: str = name  # the name of the player  todo: move into nbt
        self.gamemode: int = -1  # the current gamemode todo: move into nbt
        self.set_gamemode(1)  # and set it

        self.hearts: int = 20  # todo: move into nbt
        self.hunger: int = 20  # todo: move into nbt
        self.xp: int = 0  # todo: move into nbt
        self.xp_level: int = 0  # todo: move into nbt
        self.armor_level = 0  # todo: move into nbt
        self.armor_toughness = 0  # todo: move into nbt

        self.in_nether_portal_since = None  # todo: move into nbt
        self.should_leave_nether_portal_before_dim_change = False  # todo: move into nbt

        self.flying = False  # are we currently flying?  # todo: move into nbt

        self.fallen_since_y = -1  # how far did we fall?  # todo: move into nbt

        self.inventory_order: list = (
            [  # an ([inventoryindexname: str], [reversed slots: bool}) list
                ("hotbar", False),
                ("main", False),
            ]
        )

        self.iconparts = []

        self.active_inventory_slot: int = (
            0  # which slot is currently selected todo: move into nbt
        )

        # used for determine if we can access stuff now or must wait
        if not globals.modloader.finished:
            mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
                "stage:inventories",
                self.create_inventories,
                info="setting up player inventory",
            )
        else:
            self.create_inventories()

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:get_player_position", self.hotkey_get_position
        )
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:gamemode_1-3_toggle", self.toggle_gamemode
        )

    def hotkey_get_position(self):
        if self != globals.world.get_active_player():
            return

        import clipboard

        clipboard.copy("/tp @p {} {} {}".format(*self.position))

    def toggle_gamemode(self):
        if self != globals.world.get_active_player():
            return

        if self.gamemode == 1:
            self.set_gamemode(3)
        elif self.gamemode == 3:
            self.set_gamemode(1)

    def create_inventories(self):
        import mcpython.client.gui.InventoryCraftingTable as InvCrafting
        import mcpython.client.gui.InventoryPlayerHotbar as InvHotbar

        hotbar = self.inventories["hotbar"] = InvHotbar.InventoryPlayerHotbar()
        self.inventories[
            "main"
        ] = mcpython.client.gui.InventoryPlayerMain.InventoryPlayerMain(hotbar)
        self.inventories["chat"] = mcpython.client.chat.Chat.ChatInventory()
        self.inventories[
            "enderchest"
        ] = mcpython.client.gui.InventoryChest.InventoryChest()
        self.inventories["crafting_table"] = InvCrafting.InventoryCraftingTable()

        if mcpython.ResourceLocator.exists("build/texture/gui/icons/xp_bar_empty.png"):
            self.load_xp_icons()
        else:
            mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
                "stage:blockitemfactory:finish", self.load_xp_icons
            )

    def load_xp_icons(self):
        self.iconparts = [
            (
                mcpython.ResourceLocator.read(
                    "build/texture/gui/icons/xp_bar_empty.png", "pyglet"
                ),
                mcpython.ResourceLocator.read(
                    "build/texture/gui/icons/xp_bar.png", "pyglet"
                ),
            )
        ]

    def set_gamemode(self, gamemode: int or str):
        gamemode = self.GAMEMODE_DICT.get(gamemode, gamemode)
        # if it is a repr of the gamemode, get the int gamemode
        # else, return the int
        if gamemode == 0:
            self.flying = False
        elif gamemode == 1:
            pass
        elif gamemode == 2:
            self.flying = False
        elif gamemode == 3:
            self.flying = True
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

    def pick_up(self, itemstack: mcpython.client.gui.ItemStack.ItemStack) -> bool:
        """
        adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        if not G.eventhandler.call_cancelable(
            "gameplay:player:pick_up_item", self, itemstack
        ):
            return

        # have we an slot?
        if type(itemstack) in (
            mcpython.client.gui.Slot.Slot,
            mcpython.client.gui.Slot.SlotCopy,
        ):
            itemstack = itemstack.get_itemstack()
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
                if (
                    not slot.get_itemstack().is_empty()
                    and slot.get_itemstack().get_item_name()
                    == itemstack.get_item_name()
                    and slot.interaction_mode[2]
                ):
                    if (
                        slot.get_itemstack().item
                        and slot.get_itemstack().amount + itemstack.amount
                        <= itemstack.item.STACK_SIZE
                    ):
                        slot.get_itemstack().add_amount(itemstack.amount)
                        return True
                    else:
                        m = slot.get_itemstack().item.STACK_SIZE
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
        if "hotbar" not in self.inventories:
            self.create_inventories()
        return self.inventories["hotbar"].slots[self.active_inventory_slot]

    def kill(
        self,
        drop_items=True,
        kill_animation=True,
        damage_source: mcpython.common.entity.DamageSource.DamageSource = None,
        test_totem=True,
    ):
        if not G.eventhandler.call_cancelable(
            "gameplay:player:scheduled_die:pre",
            self,
            drop_items,
            kill_animation,
            damage_source,
            test_totem,
        ):
            return
        if test_totem:
            # todo: add effects
            if (
                self.get_active_inventory_slot().get_itemstack().get_item_name()
                == "minecraft:totem_of_undying"
            ):
                self.get_active_inventory_slot().get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
            elif (
                self.inventories["main"].slots[45].get_itemstack().get_item_name()
                == "minecraft:totem_of_undying"
            ):
                self.inventories["main"].slots[45].get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return
        super().kill()
        if not G.eventhandler.call_cancelable(
            "gameplay:player:scheduled_die:between",
            self,
            drop_items,
            kill_animation,
            damage_source,
            test_totem,
        ):
            return
        sector = mcpython.util.math.positionToChunk(self.position)
        globals.world.change_chunks(sector, None)
        self.reset_moving_slot()
        if not globals.world.gamerulehandler.table["keepInventory"].status.status:
            globals.commandparser.parse("/clear")  # todo: drop items
        if globals.world.gamerulehandler.table["showDeathMessages"].status.status:
            logger.println(
                "[CHAT] player {} died".format(self.name)
            )  # todo: add death screen
        self.set_to_spawn_point()
        self.active_inventory_slot = 0
        globals.window.dy = 0
        globals.chat.close()
        globals.inventoryhandler.close_all_inventories()
        # todo: drop xp
        self.xp = 0
        self.xp_level = 0
        self.hearts = 20
        self.hunger = 20
        self.flying = False if self.gamemode != 3 else True
        self.armor_level = 0
        self.armor_toughness = 0
        sector = mcpython.util.math.positionToChunk(self.position)
        globals.world.change_chunks(None, sector)
        # todo: recalculate armor level!

        if not globals.world.gamerulehandler.table["doImmediateRespawn"].status.status:
            globals.statehandler.switch_to(
                "minecraft:escape_state"
            )  # todo: add special state [see above]

        G.eventhandler.call("gamplay:player:die", self, damage_source)

    def _get_position(self):
        return self.position

    def _set_position(self, position):
        self.position = position

    def damage(self, hearts: int, check_gamemode=True, reason=None):
        """
        damage the player and removes the given amount of hearts (two hearts are one full displayed hart)
        """
        hearts = hearts * (
            1
            - min(
                [
                    20,
                    max(
                        [
                            self.armor_level / 5,
                            self.armor_level - hearts / (2 + self.armor_toughness / 4),
                        ]
                    ),
                ]
            )
        )
        if self.gamemode in [0, 2] or not check_gamemode:
            self.hearts -= hearts
            if self.hearts <= 0:
                self.kill()

    def reset_moving_slot(self):
        self.pick_up(globals.inventoryhandler.moving_slot.get_itemstack().copy())
        globals.inventoryhandler.moving_slot.get_itemstack().clean()

    def set_to_spawn_point(self):
        x, _, z = mcpython.util.math.normalize(self.position)
        self.position = (
            globals.world.spawnpoint[0],
            self.dimension.get_chunk_for_position(
                self.position
            ).get_maximum_y_coordinate_from_generation(x, z)
            + 3,
            globals.world.spawnpoint[1],
        )

    def tell(self, msg: str):
        if self == globals.world.get_active_player():
            globals.chat.print_ln(msg)
        else:
            pass  # todo: send through network

    def draw(self, position=None, rotation=None, full=None):
        old_position = self.position
        if position is not None:
            self.set_position_unsafe(position)
        rx, ry, rz = self.rotation if rotation is None else rotation
        rotation_whole = (0, rx + 90, 0)
        if self != globals.world.get_active_player() or full is True:
            self.RENDERER.draw(self, "outer", rotation=rotation_whole)
        else:
            if (
                self.get_active_inventory_slot() is not None
                and not self.get_active_inventory_slot().itemstack.is_empty()
            ):
                self.RENDERER.draw_box(
                    self, "right_arm_rotated", rotation=rotation_whole
                )

            if not self.inventories["main"].slots[-1].itemstack.is_empty():
                self.RENDERER.draw_box(
                    self, "left_arm_rotated", rotation=rotation_whole
                )
        self.set_position_unsafe(old_position)

    def __del__(self):
        for inventory in self.inventories.values():
            del inventory

    def __str__(self):
        return 'Player(dim={},pos={},rot={},name="{}",chunk={})'.format(
            self.dimension.id,
            self.position,
            self.rotation,
            self.name,
            self.chunk.position,
        )

    def on_inventory_cleared(self):
        self.xp = 0
        self.xp_level = 0

    def teleport(self, position, dimension=None, force_chunk_save_update=False):
        before = self.chunk.dimension if self.chunk is not None else None
        super().teleport(position, dimension, force_chunk_save_update)
        if (
            self.chunk.dimension if self.chunk is not None else None
        ) != before and self == G.world.get_active_player():
            self.chunk.dimension.world.join_dimension(self.chunk.dimension.id)
