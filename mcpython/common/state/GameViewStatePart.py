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
import math
import time
import typing

import mcpython.common.config
import mcpython.common.container.ResourceStack
import mcpython.common.item.AbstractFoodItem as ItemFood
import mcpython.common.item.AbstractToolItem as ItemTool
import mcpython.util.math
from mcpython import shared
from mcpython.common.config import GRAVITY, JUMP_SPEED, TERMINAL_VELOCITY
from mcpython.engine.physics.collision import collide
from mcpython.util.annotation import onlyInClient
from pyglet.window import key, mouse

from . import AbstractStatePart
from .InGameHotKeysManager import ALL_KEY_COMBOS


def get_block_break_time(block, itemstack):
    # todo: add factor when not on ground, when in water (when its added)

    hardness = block.HARDNESS
    is_tool = not itemstack.is_empty() and issubclass(
        type(itemstack.item), ItemTool.AbstractToolItem
    )
    tool_level = itemstack.item.TOOL_LEVEL if is_tool else 0

    if not isinstance(block.ASSIGNED_TOOLS, set):
        raise ValueError(block)

    if not is_tool or not block.ASSIGNED_TOOLS.intersection(itemstack.item.TOOL_TYPE):
        return (1.5 if block.MINIMUM_TOOL_LEVEL <= tool_level else 5) * hardness
    else:
        return (
            (1.5 if block.MINIMUM_TOOL_LEVEL <= tool_level else 5)
            * hardness
            / itemstack.item.get_speed_multiplyer(itemstack)
        )


class GameView(AbstractStatePart.AbstractStatePart):
    NAME = "minecraft:state_part_game"

    mouse_press_time = 0
    block_looking_at = None
    double_space_cooldown = 0
    set_cooldown = 0
    void_damage_cooldown = 0
    regenerate_cooldown = 0
    hunger_heart_cooldown = 0
    break_time = None

    @classmethod
    def calculate_new_break_time(cls):
        vector = shared.window.get_sight_vector()
        block_position = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )[0]
        block = (
            shared.world.get_active_dimension().get_block(block_position)
            if block_position
            else None
        )
        if not block:  # no break time because no block
            cls.break_time = None
        else:
            cls.break_time = get_block_break_time(
                block,
                shared.world.get_active_player()
                .get_active_inventory_slot()
                .get_itemstack(),
            )

    def __init__(
        self,
        activate_physics=True,
        activate_mouse=True,
        activate_keyboard=True,
        activate_3d_draw=True,
        activate_focused_block=True,
        gl_color_3d=(1.0, 1.0, 1.0),
        activate_crosshair=True,
        activate_label=True,
        clear_color=(0.5, 0.69, 1.0, 1),
        active_hotkeys=None,
    ):
        super().__init__()
        if active_hotkeys is None:
            active_hotkeys = ALL_KEY_COMBOS

        self.activate_physics = activate_physics
        self.__activate_mouse = activate_mouse
        self.activate_keyboard = activate_keyboard
        self.activate_3d_draw = activate_3d_draw
        self.activate_focused_block_draw = activate_focused_block
        self.activate_crosshair = activate_crosshair
        self.active_label = activate_label
        self.color_3d = gl_color_3d
        self.clear_color = clear_color
        self.active_hotkeys = active_hotkeys

    def set_mouse_active(self, active: bool):
        self.__activate_mouse = active
        if not active:
            [
                shared.window.mouse_pressing.__setitem__(x, False)
                for x in shared.window.mouse_pressing.keys()
            ]
        else:
            shared.world.get_active_player().reset_moving_slot()

    def get_mouse_active(self):
        return self.__activate_mouse

    activate_mouse = property(get_mouse_active, set_mouse_active)

    def create_state_renderer(self) -> typing.Any:
        from mcpython.client.state.GameViewRenderer import GameViewRenderer

        return GameViewRenderer()

    def bind_to_eventbus(self):
        state = self.master[0]
        state.eventbus.subscribe("tickhandler:general", self.on_update)
        state.eventbus.subscribe("tickhandler:general", self.on_physics_update)

        # These are the client-only events
        if shared.IS_CLIENT:
            state.eventbus.subscribe(
                "tickhandler:general", self.on_left_click_interaction_update
            )
            state.eventbus.subscribe(
                "tickhandler:general", self.on_right_click_interaction_update
            )
            state.eventbus.subscribe(
                "tickhandler:general", self.on_middle_click_interaction_update
            )
            state.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
            state.eventbus.subscribe("user:mouse:motion", self.on_mouse_motion)
            state.eventbus.subscribe("user:keyboard:press", self.on_key_press)
            state.eventbus.subscribe("user:keyboard:release", self.on_key_release)
            state.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)

    def on_update(self, dt: float):
        if shared.IS_CLIENT:
            for hotkey in self.active_hotkeys:
                hotkey.check()

            # do counting stuff  todo: change to per-mouse-button
            if any(shared.window.mouse_pressing.values()):
                self.mouse_press_time += dt

            if (
                shared.window.exclusive
                and any(shared.window.mouse_pressing.values())
                and time.time() - self.set_cooldown > 1
            ):
                vector = shared.window.get_sight_vector()
                block_position, previous, hit_position = shared.world.hit_test(
                    shared.world.get_active_player().position, vector
                )
                if block_position:
                    if (
                        block_position != self.block_looking_at
                    ):  # have we changed the block we were looking at?
                        self.block_looking_at = block_position
                        self.mouse_press_time = 0

                if not self.break_time:
                    self.calculate_new_break_time()

    def on_physics_update(self, dt: float):
        if not self.activate_physics:
            return

        m = 8
        dt = min(dt, 0.2)

        if shared.IS_CLIENT:
            player = shared.world.get_active_player()

            for _ in range(m):
                self.physics_update_internal(dt / m, player)

            player.send_update_package_when_client()
        else:
            pass
            # for player in shared.world.players.values():
            #     for _ in range(m):
            #         self.physics_update_internal(dt / m, player)

    def on_left_click_interaction_update(self, dt: float):
        if shared.window.exclusive and shared.window.mouse_pressing[mouse.LEFT]:

            player = shared.world.get_active_player()

            vector = shared.window.get_sight_vector()
            block_position, previous, hit_position = shared.world.hit_test(
                player.position, vector
            )

            if block_position:
                if self.break_time is None:
                    self.calculate_new_break_time()

                chunk = shared.world.get_active_dimension().get_chunk(
                    *mcpython.util.math.position_to_chunk(block_position)
                )

                if player.gamemode == 1:
                    if self.mouse_press_time >= 0.10:
                        # todo: check for special break behaviour (chests, etc.)
                        chunk.remove_block(block_position)

                elif player.gamemode in (0, 2):
                    selected_itemstack: mcpython.common.container.ResourceStack.ItemStack = (
                        player.get_active_inventory_slot().get_itemstack()
                    )

                    block = shared.world.get_active_dimension().get_block(
                        block_position, none_if_str=True
                    )
                    if block is None:
                        return

                    if self.mouse_press_time >= self.break_time and block.IS_BREAKABLE:

                        if (
                            not selected_itemstack.is_empty()
                            and not selected_itemstack.item.check_can_destroy(
                                block, player
                            )
                        ):
                            return

                        if shared.world.gamerule_handler.table[
                            "doTileDrops"
                        ].status.status:
                            items = shared.loot_table_handler.get_drop_for_block(
                                block, player=player
                            )
                            [
                                block.on_request_item_for_block(itemstack)
                                for itemstack in items
                            ]
                            player.pick_up_item(items)

                        chunk.remove_block(block_position)

                        if not selected_itemstack.is_empty():
                            selected_itemstack.item.on_block_broken_with(
                                selected_itemstack, player, block
                            )

    def on_right_click_interaction_update(self, dt: float):
        if not shared.window.mouse_pressing[mouse.RIGHT]:
            return

        player = shared.world.get_active_player()
        slot = player.get_active_inventory_slot()
        active_itemstack = slot.get_itemstack()

        if shared.window.exclusive and time.time() - self.set_cooldown > 1:
            if not active_itemstack.is_empty() and isinstance(
                active_itemstack.item, ItemFood.AbstractFoodItem
            ):
                food = active_itemstack.item
                if food.on_eat(active_itemstack):
                    self.set_cooldown = time.time() - 1
                    return

            vector = shared.window.get_sight_vector()
            block_position, previous, hit_position = shared.world.hit_test(
                player.position, vector
            )

            if block_position and previous:
                if (
                    active_itemstack.item
                    and active_itemstack.item.HAS_BLOCK
                    and self.mouse_press_time > 0.10
                    and player.gamemode in (0, 1, 2)
                ):
                    x, y, z = previous
                    px, _, pz = mcpython.util.math.normalize(player.position)
                    py = math.ceil(player.position[1])

                    # Check if the block is in the player todo: use the bounding box
                    if not (
                        x == px and z == pz and py - 1 <= y <= py
                    ) and not shared.world.get_active_dimension().get_block(
                        previous, none_if_str=True
                    ):
                        chunk = (
                            shared.world.get_active_dimension().get_chunk_for_position(
                                previous, generate=False
                            )
                        )

                        if not active_itemstack.item.check_can_be_set_on(
                            chunk.get_block(block_position), player
                        ):
                            self.mouse_press_time = 0
                            return

                        instance = chunk.add_block(
                            previous,
                            slot.get_itemstack().item.get_block(),
                            lazy_setup=lambda block: block.set_creation_properties(
                                set_to=block_position,
                                real_hit=hit_position,
                                player=player,
                            ),
                        )

                        active_itemstack.item.on_set_from_item(instance)

                        if player.gamemode == 0:
                            slot.get_itemstack().add_amount(-1)

                        self.mouse_press_time = 0

    def on_middle_click_interaction_update(self, dt: float):
        player = shared.world.get_active_player()
        if (
            shared.window.exclusive
            and shared.window.mouse_pressing[mouse.MIDDLE]
            and time.time() - self.set_cooldown > 1
        ):
            vector = shared.window.get_sight_vector()
            block_position, previous, hit_position = shared.world.hit_test(
                player.position, vector
            )

            if block_position and self.mouse_press_time > 0.1:
                chunk = shared.world.get_active_dimension().get_chunk_for_position(
                    block_position
                )
                self.mouse_press_time = 0
                block = shared.world.get_active_dimension().get_block(block_position)
                itemstack = mcpython.common.container.ResourceStack.ItemStack(
                    block.NAME if type(block) != str else block
                )
                block = chunk.get_block(block_position)
                if block:
                    block.on_request_item_for_block(itemstack)
                selected_slot = player.get_active_inventory_slot()

                for inventory, reverse in player.inventory_order:
                    slots = inventory.slots
                    if reverse:
                        slots.reverse()

                    for slot in slots:
                        if (
                            slot.get_itemstack().item
                            and slot.get_itemstack().item.HAS_BLOCK
                            and slot.get_itemstack().item == itemstack.item
                        ):
                            if inventory != "hotbar":
                                ref_itemstack = selected_slot.get_itemstack()
                                selected_slot.set_itemstack(slot.get_itemstack())
                                slot.set_itemstack(ref_itemstack)
                            else:
                                player.set_active_inventory_slot(slots.index(slot))
                            return

                if player.gamemode == 1:
                    old_itemstack = selected_slot.get_itemstack()
                    selected_slot.set_itemstack(itemstack)
                    player.pick_up_item(old_itemstack)
                    if shared.window.mouse_pressing[mouse.LEFT]:
                        self.calculate_new_break_time()

    def physics_update_internal(self, dt: float, player):
        """
        Internal implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        todo: on server, do for all players

        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """

        # todo: add check game hardness != friendly
        if player.gamemode in (0, 2) and shared.window.keys[key.LSHIFT]:
            player.hunger -= dt * 0.2

        dx, dy, dz = self.calculate_motion(dt, player)

        # collisions & position update
        x, y, z = player.position
        before = mcpython.util.math.position_to_chunk(player.position)
        if player.gamemode != 3:
            x, y, z = collide((x + dx, y + dy, z + dz), 2, player.position)
        else:
            x, y, z = x + dx, y + dy, z + dz

        if shared.IS_CLIENT and shared.window.dy < 0 and player.fallen_since_y is None:
            player.fallen_since_y = player.position[1]

        player.position = (x, y, z)

        # If below y=-10, and he has flown more than the cooldown, he should get damaged
        # todo: add property for y level
        if y < -10 and time.time() - self.void_damage_cooldown > 0.25:
            player.damage(1)
            self.void_damage_cooldown = time.time()

        # todo: this does not perform well, can we activate it again somewhere in the future?
        # self.update_player_chunks(before, player)
        self.calculate_player_hearts(dt, player)

    def calculate_player_hearts(self, dt, player):
        if (
            player.hearts < 20
            and player.hunger > 4
            and time.time() - self.regenerate_cooldown > 2
            and player.gamemode in (0, 2)
        ):
            player.hearts += 1
            player.hunger -= 0.5
            self.regenerate_cooldown = time.time()

        if player.hunger == 0 and time.time() - self.hunger_heart_cooldown > 1:
            player.damage(1)
            self.hunger_heart_cooldown = time.time()

        nx, _, nz = mcpython.util.math.normalize(player.position)
        ny = math.ceil(player.position[1])

        block = shared.world.get_active_dimension().get_block(
            (nx, ny, nz), none_if_str=True
        )
        if player.gamemode in (0, 2) and block and block.IS_SOLID:
            player.damage(dt)

    def update_player_chunks(self, before, player):
        after = mcpython.util.math.position_to_chunk(player.position)
        if before != after:
            shared.world.change_chunks(before, after)

    def calculate_motion(self, dt: float, player) -> typing.Tuple[float, float, float]:

        # todo: add a way to do stuff here!
        if not shared.IS_CLIENT:
            return 0, 0, 0

        speed = mcpython.common.config.SPEED_DICT[player.gamemode][
            (0 if not shared.window.keys[key.LSHIFT] else 1)
            + (0 if not player.flying else 2)
        ]

        if not player.flying and shared.window.dy == 0:
            x, y, z = mcpython.util.math.normalize(player.position)
            block_inst = shared.world.get_active_dimension().get_block((x, y - 2, z))
            if (
                block_inst is not None
                and type(block_inst) != str
                and block_inst.CUSTOM_WALING_SPEED_MULTIPLIER is not None
            ):
                speed *= block_inst.CUSTOM_WALING_SPEED_MULTIPLIER

        d = dt * speed  # distance covered this tick.
        dx, dy, dz = player.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not player.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            shared.window.dy -= dt * GRAVITY
            shared.window.dy = max(shared.window.dy, -TERMINAL_VELOCITY)
            dy += shared.window.dy * dt
        elif self.activate_keyboard and not (
            shared.window.keys[key.SPACE] and shared.window.keys[key.LSHIFT]
        ):
            dy = (
                dt * 6
                if shared.window.keys[key.SPACE]
                else (-dt * 6 if shared.window.keys[key.LSHIFT] else 0)
            )
        return dx, dy, dz

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        player = shared.world.get_active_player()
        if not self.activate_mouse:
            return

        slot = player.get_active_inventory_slot()
        vector = shared.window.get_sight_vector()
        block_position, previous, hit_position = shared.world.hit_test(
            player.position, vector
        )
        block = (
            shared.world.get_active_dimension().get_block(
                block_position, none_if_str=True
            )
            if block_position
            else None
        )
        cancel = False

        if not slot.get_itemstack().is_empty():
            if slot.get_itemstack().item.on_player_interact(
                player,
                block,
                button,
                modifiers,
                slot.get_itemstack(),
                previous,
            ):
                cancel = True

        if block:
            if not cancel and block.on_player_interaction(
                player,
                button,
                modifiers,
                hit_position,
                player.get_active_inventory_slot().get_itemstack(),
            ):
                cancel = True

        if cancel:
            self.set_cooldown = time.time()
            shared.window.mouse_pressing[button] = False
        else:
            self.calculate_new_break_time()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        vector = shared.window.get_sight_vector()
        previous_block = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )[0]

        if shared.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y, _ = shared.world.get_active_player().rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            shared.world.get_active_player().rotation = (x, y, 0)
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

            vector = shared.window.get_sight_vector()
            new_block = shared.world.hit_test(
                shared.world.get_active_player().position, vector
            )[0]

            if previous_block and new_block != previous_block:
                self.mouse_press_time = 0

    def on_key_press(self, symbol: int, modifiers: int):
        player = shared.world.get_active_player()

        if not self.activate_keyboard:
            return

        # does a hotkey override this key?
        for hotkey in self.active_hotkeys:
            if hotkey.blocks(symbol, modifiers):
                return

        if shared.state_handler.global_key_bind_toggle:
            return

        if symbol == key.W and not shared.window.keys[key.S]:
            player.strafe[0] = -1
        elif symbol == key.S and not shared.window.keys[key.W]:
            player.strafe[0] = 1
        elif symbol == key.A and not shared.window.keys[key.D]:
            player.strafe[1] = -1
        elif symbol == key.D and not shared.window.keys[key.A]:
            player.strafe[1] = 1

        elif (
            symbol == key.SPACE
            and player.inventory_chat not in shared.inventory_handler.open_containers
        ):
            if (
                self.double_space_cooldown
                and time.time() - self.double_space_cooldown < 0.5
                and player.gamemode == 1
            ):
                player.flying = not player.flying
                self.double_space_cooldown = None
            else:
                if shared.window.dy == 0:
                    shared.window.dy = player.get_jump_speed()

        elif symbol in shared.window.num_keys and not modifiers & key.MOD_SHIFT:
            index = symbol - shared.window.num_keys[0]
            player.set_active_inventory_slot(index)
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_key_release(self, symbol: int, modifiers: int):
        if not self.activate_keyboard:
            return

        player = shared.world.get_active_player()

        # todo: make this configurable
        if symbol == key.W:
            player.strafe[0] = 0 if not shared.window.keys[key.S] else 1
        elif symbol == key.S:
            player.strafe[0] = 0 if not shared.window.keys[key.W] else -1
        elif symbol == key.A:
            player.strafe[1] = 0 if not shared.window.keys[key.D] else 1
        elif symbol == key.D:
            player.strafe[1] = 0 if not shared.window.keys[key.A] else -1
        elif symbol == key.SPACE:
            self.double_space_cooldown = time.time()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if self.activate_mouse and shared.window.exclusive:
            player = shared.world.get_active_player()

            player.active_inventory_slot -= scroll_y
            player.active_inventory_slot = round(abs(player.active_inventory_slot % 9))
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()
