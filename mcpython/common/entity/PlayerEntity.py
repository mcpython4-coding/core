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
import typing

import mcpython.client.gui.Slot
import mcpython.client.rendering.entities.EntityRenderer
import mcpython.common.container.ResourceStack
import mcpython.common.entity.AbstractEntity
import mcpython.common.entity.DamageSource
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
import mcpython.util.math
from mcpython import shared
from mcpython.common.network.packages.PlayerInfoPackages import PlayerUpdatePackage
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


@shared.registry
class PlayerEntity(mcpython.common.entity.AbstractEntity.AbstractEntity):
    RENDERER = None

    @classmethod
    def init_renderers(cls):
        cls.RENDERER = mcpython.client.rendering.entities.EntityRenderer.EntityRenderer(
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
        self.is_in_init = True
        super().__init__(dimension=dimension)

        if name is None:
            raise RuntimeError("name cannot be None")

        self.name: str = name  # the name of the player
        self.gamemode: int = -1  # the current gamemode

        self.hearts: int = 20
        self.hunger: float = 20
        self.xp: int = 0
        self.xp_level: int = 0
        self.armor_level: float = 0
        self.armor_toughness: float = 0

        self.in_nether_portal_since: typing.Optional[float] = None
        self.should_leave_nether_portal_before_dim_change = False

        # are we currently flying?
        self.flying = False

        # how far did we fall?
        self.fallen_since_y: float = -1

        # which slot is currently selected
        self.active_inventory_slot: int = 0

        # the different parts of the player inventory
        # todo: use only containers here
        self.inventories_created = False
        self.inventory_hotbar = None
        self.inventory_main = None
        self.inventory_enderchest = None
        self.inventory_chat = None
        self.inventory_crafting_table = None

        # used for determine if we can access stuff now or must wait
        # todo: can we do something else
        if not shared.mod_loader.finished:
            shared.mod_loader["minecraft"].eventbus.subscribe(
                "stage:inventories",
                self.create_inventories,
                info="setting up player inventory",
            )

        else:
            self.create_inventories()

        # todo: move to somewhere else! (Each player creation does a new one!)
        # todo: client-only
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:get_player_position", self.hotkey_get_position
        )
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:gamemode_1-3_toggle", self.toggle_gamemode
        )

        # the lookup order of inventory, todo: move to inventory handler
        self.inventory_order = []
        self.set_gamemode(1)

        self.is_in_init = False

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)

        buffer.write_string(self.name)
        buffer.write_int(self.gamemode)
        buffer.write_int(self.hearts)
        buffer.write_float(self.hunger)
        buffer.write_int(self.xp)
        buffer.write_long(self.xp_level)
        buffer.write_float(self.armor_level)
        buffer.write_float(self.armor_toughness)
        buffer.write_bool(self.flying)
        buffer.write_float(self.fallen_since_y)
        buffer.write_int(self.active_inventory_slot)

        self.create_inventories()
        self.inventory_hotbar.write_to_network_buffer(buffer)
        self.inventory_main.write_to_network_buffer(buffer)
        self.inventory_enderchest.write_to_network_buffer(buffer)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)

        self.name = buffer.read_string()
        self.gamemode = buffer.read_int()
        self.hearts = buffer.read_int()
        self.hunger = buffer.read_float()
        self.xp = buffer.read_int()
        self.xp_level = buffer.read_long()
        self.armor_level = buffer.read_float()
        self.armor_toughness = buffer.read_float()
        self.flying = buffer.read_bool()
        self.fallen_since_y = buffer.read_float()
        self.active_inventory_slot = buffer.read_int()

        self.create_inventories()
        self.inventory_hotbar.read_from_network_buffer(buffer)
        self.inventory_main.read_from_network_buffer(buffer)
        self.inventory_enderchest.read_from_network_buffer(buffer)

        return self

    def create_update_package(self) -> PlayerUpdatePackage:
        package = PlayerUpdatePackage()
        package.name = self.name
        package.position, package.rotation, package.motion = (
            self.position,
            self.rotation,
            self.nbt_data["motion"],
        )
        package.dimension = self.dimension.get_name()
        package.selected_slot = self.active_inventory_slot
        package.gamemode = self.gamemode

        return package

    def write_update_package(self, package: PlayerUpdatePackage):
        self.position, self.rotation, self.nbt_data["motion"] = (
            package.position,
            package.rotation,
            package.motion,
        )
        self.dimension = shared.world.get_dimension_by_name(package.dimension)
        self.active_inventory_slot = package.selected_slot
        self.gamemode = package.gamemode

        return self

    def send_update_package_when_client(self):
        if shared.IS_CLIENT and shared.IS_NETWORKING and not self.is_in_init:
            shared.NETWORK_MANAGER.send_package(self.create_update_package(), 0)

    def hotkey_get_position(self):
        # todo: remove this check when only the current player uses this event
        if self != shared.world.get_active_player():
            return

        import clipboard

        clipboard.copy("/tp @p {} {} {}".format(*self.position))

    def toggle_gamemode(self):
        """
        Toggles between gamemode 1 and 3, used internally for the hotkey F3+N
        """
        # todo: remove this check
        if self != shared.world.get_active_player():
            return

        if self.gamemode == 1:
            self.set_gamemode(3)
        elif self.gamemode == 3:
            self.set_gamemode(1)

    def create_inventories(self):
        """
        Helper method for setting up the player inventory
        todo: can we re-use inventories from previous players?
        """
        if self.inventories_created:
            return
        self.inventories_created = True

        import mcpython.client.Chat as Chat
        import mcpython.client.gui.InventoryChest as Chest
        import mcpython.client.gui.InventoryCraftingTable as InvCrafting
        import mcpython.client.gui.InventoryPlayerHotbar as InvHotbar
        import mcpython.client.gui.MainPlayerInventory as Main

        self.inventory_hotbar = InvHotbar.InventoryPlayerHotbar.create(self)
        self.inventory_main = Main.MainPlayerInventory.create(self.inventory_hotbar)
        self.inventory_chat = Chat.ChatInventory()
        self.inventory_enderchest = Chest.InventoryChest()
        self.inventory_crafting_table = InvCrafting.InventoryCraftingTable()

        self.inventory_order = [
            (self.inventory_hotbar, False),
            (self.inventory_main, False),
        ]

    def init_creative_tabs(self):
        import mcpython.client.gui.InventoryCreativeTab

    def set_gamemode(self, gamemode: typing.Union[int, str]):
        """
        Sets the player game-modes and the assigned properties
        todo: something better here?
        """
        if str(gamemode) in self.GAMEMODE_DICT:
            gamemode = self.GAMEMODE_DICT[str(gamemode)]

            if not shared.event_handler.call_cancelable(
                "player:gamemode_change", self, self.gamemode, gamemode
            ):
                return

            if gamemode == 0:
                self.flying = False
            elif gamemode == 1:
                pass
            elif gamemode == 2:
                self.flying = False
            elif gamemode == 3:
                self.flying = True

            self.gamemode = gamemode
        else:
            # todo: add an option to raise an exception here
            logger.println("[ERROR] invalid gamemode:", gamemode)
        self.send_update_package_when_client()

    def get_needed_xp_for_next_level(self) -> int:
        """
        :return: the xp amount needed to reach the next xp level
        """
        if self.xp_level < 16:
            return self.xp_level * 2 + 5
        elif self.xp_level < 30:
            return 37 + (self.xp_level - 15) * 5
        else:
            return 107 + (self.xp_level - 29) * 9

    def add_xp(self, xp: int):
        while xp > 0:
            needed = self.get_needed_xp_for_next_level()
            if self.xp + xp < needed:
                self.xp += xp
                return self
            elif xp > needed:
                xp -= needed
                self.xp_level += 1
            else:
                xp = xp - (needed - self.xp)
                self.xp_level += 1
        self.send_update_package_when_client()
        return self

    def add_xp_level(self, xp_levels: int):
        self.xp_level += xp_levels
        self.send_update_package_when_client()
        return self

    def clear_xp(self):
        self.xp_level = 0
        self.xp = 0
        self.send_update_package_when_client()
        return self

    def pick_up_item(
        self,
        itemstack: typing.Union[
            mcpython.common.container.ResourceStack.ItemStack,
            mcpython.client.gui.Slot.Slot,
        ],
    ) -> bool:
        """
        Adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        if not shared.event_handler.call_cancelable(
            "gameplay:player:pick_up_item", self, itemstack
        ):
            return False

        # have we an slot?
        if isinstance(itemstack, mcpython.client.gui.Slot.Slot):
            itemstack = itemstack.get_itemstack()
        if type(itemstack) == list:
            return all([self.pick_up_item(itemstack) for itemstack in itemstack])

        if not itemstack.item or itemstack.amount == 0:
            return True
        for inventory, reverse in self.inventory_order:
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
        for inventory, reverse in self.inventory_order:
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if not slot.get_itemstack().item and slot.interaction_mode[2]:
                    slot.set_itemstack(itemstack)
                    return True
        return False

    def set_active_inventory_slot(self, slot: int):
        """
        Sets the active inventory slot by ID (0-8)
        Clamped in the range when out of range
        """
        self.active_inventory_slot = max(min(round(slot), 8), 0)
        self.send_update_package_when_client()
        return self

    def get_active_inventory_slot(self):
        """
        Gets the slot of the selected slot
        """
        if self.inventory_hotbar is None:
            self.create_inventories()

        return self.inventory_hotbar.slots[self.active_inventory_slot]

    def kill(
        self,
        drop_items=True,
        kill_animation=True,
        damage_source: mcpython.common.entity.DamageSource.DamageSource = None,
        test_totem=True,
        force=False,
        internal=False,
    ):
        if test_totem and not force:
            # todo: add effects of totem
            # todo: add list to player of possible slots with possibility of being callable
            # todo: add tag for this functionality
            a = (
                self.get_active_inventory_slot().get_itemstack().get_item_name()
                == "minecraft:totem_of_undying"
            )
            b = (
                self.inventory_main.slots[45].get_itemstack().get_item_name()
                == "minecraft:totem_of_undying"
            )
            if (a or b) and not shared.event_handler.call_cancelable(
                "player:totem_used", self
            ):
                if a:
                    self.get_active_inventory_slot().get_itemstack().clean()
                else:
                    self.inventory_main.slots[45].get_itemstack().clean()
                self.hearts = 20
                self.hunger = 20
                return

        super().kill()

        # We don't need them anymore? todo: this feels wrong!
        self.inventory_main.free()
        self.inventory_hotbar.free()

        sector = mcpython.util.math.position_to_chunk(self.position)
        shared.world.change_chunks(sector, None)
        self.reset_moving_slot()
        if (
            not shared.world.gamerule_handler.table["keepInventory"].status.status
            or internal
        ):
            for inventory in self.get_inventories():  # iterate over all inventories ...
                inventory.clear()  # ... and clear them

        if (
            shared.world.gamerule_handler.table["showDeathMessages"].status.status
            and not internal
        ):
            logger.println(
                "[CHAT] player {} died".format(self.name)
            )  # todo: add death screen and death type

        if not internal:
            self.teleport_to_spawn_point()

        self.active_inventory_slot = 0

        if shared.IS_CLIENT:
            shared.window.dy = 0
            shared.chat.close()
            shared.inventory_handler.close_all_inventories()

        # todo: drop parts of the xp
        self.xp = 0
        self.xp_level = 0
        self.hearts = 20
        self.hunger = 20
        self.flying = False if self.gamemode != 3 else True  # todo: add event for this
        self.armor_level = 0
        self.armor_toughness = 0

        if shared.IS_CLIENT:
            sector = mcpython.util.math.position_to_chunk(self.position)
            shared.world.change_chunks(None, sector)

        # todo: recalculate armor level!

        if (
            not shared.world.gamerule_handler.table["doImmediateRespawn"].status.status
            and not internal
        ):
            # todo: add special state [see above]
            shared.state_handler.change_state("minecraft:escape_menu")

        if not internal:
            shared.event_handler.call("gameplay:player:die", self, damage_source)

        self.send_update_package_when_client()

    def _get_position(self):
        return self.position

    def _set_position(self, position):
        self.position = position

    def damage(self, hearts: int, check_gamemode=True, reason=None):
        """
        Damage the player and removes the given amount of hearts (two hearts are one full displayed hart)
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
        stack = shared.inventory_handler.moving_slot.get_itemstack()
        self.pick_up_item(stack.copy())
        stack.clean()

    def teleport_to_spawn_point(self):
        # todo: is there a better way?
        if self.dimension is None:
            self.dimension = shared.world.get_dimension(0)

        x, _, z = mcpython.util.math.normalize(self.position)
        h = self.dimension.get_chunk_for_position(
            self.position
        ).get_maximum_y_coordinate_from_generation(x, z)

        if h is None:
            logger.println(
                f"[WARN] cannot find spawn height at {x} {z}. Using '255' as default"
            )
            h = 255

        self.position = (
            shared.world.spawn_point[0],
            h + 3,
            shared.world.spawn_point[1],
        )

    def tell(self, msg: str):
        if not shared.IS_CLIENT:
            shared.NETWORK_MANAGER.send_to_player_chat(self.name, msg)
            return

        if self == shared.world.get_active_player():
            shared.chat.print_ln(msg)
        else:
            shared.NETWORK_MANAGER.send_to_player_chat(self.name, msg)

    def draw(self, position=None, rotation=None, full=None):
        old_position = self.position
        if position is not None:
            self.set_position_unsafe(position)

        rx, ry, rz = self.rotation if rotation is None else rotation
        rotation_whole = (0, rx + 90, 0)

        if self != shared.world.get_active_player() or full is True:
            self.RENDERER.draw(self, "outer", rotation=rotation_whole)

        else:
            if (
                self.get_active_inventory_slot() is not None
                and not self.get_active_inventory_slot().itemstack.is_empty()
            ):
                self.RENDERER.draw_box(
                    self, "right_arm_rotated", rotation=rotation_whole
                )

            if not self.inventory_main.slots[-1].itemstack.is_empty():
                self.RENDERER.draw_box(
                    self, "left_arm_rotated", rotation=rotation_whole
                )

        self.set_position_unsafe(old_position)

    def __str__(self):
        return 'Player(dim={},pos={},rot={},name="{}",chunk={})'.format(
            self.dimension.id if self.dimension is not None else "N/A",
            self.position,
            self.rotation,
            self.name,
            self.chunk.position if self.chunk is not None else "N/A",
        )

    def on_inventory_cleared(self):
        self.xp = 0
        self.xp_level = 0

    def teleport(self, position, dimension=None, force_chunk_save_update=False):
        before = self.chunk.dimension if self.chunk is not None else None
        super().teleport(position, dimension, force_chunk_save_update)
        # todo: this seems not good...
        if (
            self.chunk.dimension if self.chunk is not None else None
        ) != before and self == shared.world.get_active_player():
            self.chunk.dimension.world.join_dimension(self.chunk.dimension.id)

    # General API
    def get_inventories(self) -> list:
        return [self.inventory_main, self.inventory_hotbar]
