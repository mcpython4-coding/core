"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from . import StatePart
from mcpython import shared
from mcpython.common.config import FLYING_SPEED, GRAVITY, TERMINAL_VELOCITY, JUMP_SPEED
from pyglet.window import key, mouse
import pyglet
import mcpython.common.container.ItemStack
import mcpython.common.config
import mcpython.util.math
import time
import mcpython.common.item.AbstractFoodItem as ItemFood
import mcpython.common.item.AbstractToolItem as ItemTool
import math
import enum
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class HotKeys(enum.Enum):
    # from https://minecraft.gamepedia.com/Debug_screen

    RELOAD_CHUNKS = ([key.F3, key.A], "hotkey:chunk_reload")
    GAME_CRASH = ([key.F3, key.C], "hotkey:game_crash", 10)
    GET_PLAYER_POSITION = ([key.F3, key.C], "hotkey:get_player_position")
    CLEAR_CHAT = ([key.F3, key.D], "hotkey:clear_chat")
    COPY_BLOCK_OR_ENTITY_DATA = ([key.F3, key.I], "hotkey:copy_block_or_entity_data")
    TOGGLE_GAMEMODE_1_3 = ([key.F3, key.N], "hotkey:gamemode_1-3_toggle")
    RELOAD_TEXTURES = ([key.F3, key.T], "hotkey:reload_textures")

    def __init__(self, keys, event, min_press=0):
        self.keys = keys
        self.event = event
        self.active = False
        self.min_press = min_press
        self.press_start = 0

    def check(self):
        status = all([shared.window.keys[symbol] for symbol in self.keys])
        if self.active and not status:
            self.active = False
            if time.time() - self.press_start < self.min_press:
                return
            shared.event_handler.call(self.event)
        if not self.active and status:
            self.active = True
            self.press_start = time.time()

    def blocks(self, symbol, mods) -> bool:
        return (
            symbol in self.keys and self.check()
        )  # is this key a) affected by this and b) is our combo active


ALL_KEY_COMBOS = [
    HotKeys.RELOAD_CHUNKS,
    HotKeys.GAME_CRASH,
    HotKeys.GET_PLAYER_POSITION,
    HotKeys.CLEAR_CHAT,
    HotKeys.COPY_BLOCK_OR_ENTITY_DATA,
    HotKeys.TOGGLE_GAMEMODE_1_3,
    HotKeys.RELOAD_TEXTURES,
]


@onlyInClient()
class StatePartGame(StatePart.StatePart):
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
        blockpos = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )[0]
        block = (
            shared.world.get_active_dimension().get_block(blockpos)
            if blockpos
            else None
        )
        if not block:
            cls.break_time = None  # no break time because no block
        else:
            hardness = block.HARDNESS
            itemstack = (
                shared.world.get_active_player()
                .get_active_inventory_slot()
                .get_itemstack()
                .copy()
            )
            is_tool = not itemstack.is_empty() and issubclass(
                type(itemstack.item), ItemTool.AbstractToolItem
            )
            tool_level = itemstack.item.TOOL_LEVEL if is_tool else 0
            if not is_tool or not any(
                [x in block.ASSIGNED_TOOLS for x in itemstack.item.TOOL_TYPE]
            ):
                cls.break_time = (
                    1.5 if block.MINIMUM_TOOL_LEVEL <= tool_level else 5
                ) * hardness
            else:
                cls.break_time = (
                    (1.5 if block.MINIMUM_TOOL_LEVEL <= tool_level else 5)
                    * hardness
                    / itemstack.item.get_speed_multiplyer(itemstack)
                )
            # todo: add factor when not on ground, when in water (when its added)

    def __init__(
        self,
        activate_physics=True,
        activate_mouse=True,
        activate_keyboard=True,
        activate_3d_draw=True,
        activate_focused_block=True,
        glcolor3d=(1.0, 1.0, 1.0),
        activate_crosshair=True,
        activate_lable=True,
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
        self.active_lable = activate_lable
        self.color_3d = glcolor3d
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

    def bind_to_eventbus(self):
        state = self.master[0]
        state.eventbus.subscribe("gameloop:tick:end", self.on_update)
        state.eventbus.subscribe("gameloop:tick:end", self.on_physics_update)
        state.eventbus.subscribe(
            "gameloop:tick:end", self.on_left_click_interaction_update
        )
        state.eventbus.subscribe(
            "gameloop:tick:end", self.on_right_click_interaction_update
        )
        state.eventbus.subscribe(
            "gameloop:tick:end", self.on_middle_click_interaction_update
        )
        state.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        state.eventbus.subscribe("user:mouse:motion", self.on_mouse_motion)
        state.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        state.eventbus.subscribe("user:keyboard:release", self.on_key_release)
        state.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)
        state.eventbus.subscribe("render:draw:3d", self.on_draw_3d)
        state.eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def on_update(self, dt: float):
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
            blockpos, previous, hitpos = shared.world.hit_test(
                shared.world.get_active_player().position, vector
            )
            if blockpos:
                if (
                    blockpos != self.block_looking_at
                ):  # have we changed the block we were looking at?
                    self.block_looking_at = blockpos
                    self.mouse_press_time = 0

            if not self.break_time:
                self.calculate_new_break_time()

    def on_physics_update(self, dt: float):
        if not self.activate_physics:
            return
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)

    def on_left_click_interaction_update(self, dt: float):
        if self.break_time is None:
            self.calculate_new_break_time()

        player = shared.world.get_active_player()
        selected_itemstack: mcpython.common.container.ItemStack.ItemStack = (
            player.get_active_inventory_slot().get_itemstack()
        )
        if (
            shared.window.exclusive
            and any(shared.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            vector = shared.window.get_sight_vector()
            blockpos, previous, hit_position = shared.world.hit_test(
                player.position, vector
            )
            if shared.window.mouse_pressing[mouse.LEFT] and blockpos:
                block = shared.world.get_active_dimension().get_block(blockpos)
                if block is None:
                    return

                chunk = shared.world.get_active_dimension().get_chunk(
                    *mcpython.util.math.position_to_chunk(blockpos)
                )

                if player.gamemode == 1:
                    if self.mouse_press_time >= 0.10:
                        chunk.remove_block(blockpos)
                        chunk.on_block_updated(blockpos)
                        chunk.check_neighbors(blockpos)
                elif player.gamemode in (0, 2):
                    if (
                        not isinstance(block, str)
                        and self.mouse_press_time >= self.break_time
                        and block.IS_BREAKABLE
                    ):
                        if (
                            not selected_itemstack.is_empty()
                            and selected_itemstack.item.check_can_destroy(block, player)
                        ) or (selected_itemstack.is_empty() and player.gamemode == 2):
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

                        chunk.remove_block(blockpos)
                        chunk.on_block_updated(blockpos)
                        chunk.check_neighbors(blockpos)

                        if not selected_itemstack.is_empty():
                            selected_itemstack.item.on_block_broken_with(
                                selected_itemstack, player, block
                            )

    def on_right_click_interaction_update(self, dt: float):
        player = shared.world.get_active_player()
        active_itemstack = player.get_active_inventory_slot().get_itemstack()
        if (
            shared.window.exclusive
            and any(shared.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            if active_itemstack.item and isinstance(
                active_itemstack.item,
                ItemFood.AbstractFoodItem,
            ):
                item_food = active_itemstack.item
                if item_food.on_eat():
                    self.set_cooldown = time.time() - 1
                    active_itemstack.add_amount(-1)
                    return
            vector = shared.window.get_sight_vector()
            blockpos, previous, hit_position = shared.world.hit_test(
                player.position, vector
            )
            if blockpos:
                if shared.window.mouse_pressing[mouse.RIGHT] and previous:
                    slot = player.get_active_inventory_slot()
                    if (
                        slot.get_itemstack().item
                        and slot.get_itemstack().item.HAS_BLOCK
                        and self.mouse_press_time > 0.10
                        and player.gamemode in (0, 1, 2)
                    ):
                        x, y, z = previous
                        px, _, pz = mcpython.util.math.normalize(player.position)
                        py = math.ceil(player.position[1])
                        if not (
                            x == px and z == pz and py - 1 <= y <= py
                        ) and not shared.world.get_active_dimension().get_block(
                            previous
                        ):
                            chunk = shared.world.get_active_dimension().get_chunk_for_position(
                                previous
                            )

                            if not slot.get_itemstack().item.check_can_be_set_on(
                                chunk.get_block(blockpos), player
                            ):
                                self.mouse_press_time = 0
                                return

                            instance = chunk.add_block(
                                previous,
                                slot.get_itemstack().item.get_block(),
                                lazy_setup=lambda block: block.set_creation_properties(
                                    set_to=blockpos,
                                    real_hit=hit_position,
                                    player=player,
                                ),
                            )

                            chunk.on_block_updated(previous)
                            slot.get_itemstack().item.on_set_from_item(instance)
                            if player.gamemode == 0:
                                slot.get_itemstack().add_amount(-1)
                            self.mouse_press_time = 0

    def on_middle_click_interaction_update(self, dt: float):
        player = shared.world.get_active_player()
        if (
            shared.window.exclusive
            and any(shared.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            vector = shared.window.get_sight_vector()
            blockpos, previous, hitpos = shared.world.hit_test(player.position, vector)
            if (
                shared.window.mouse_pressing[mouse.MIDDLE]
                and blockpos
                and self.mouse_press_time > 0.1
            ):
                chunk = shared.world.get_active_dimension().get_chunk_for_position(
                    blockpos
                )
                self.mouse_press_time = 0
                block = shared.world.get_active_dimension().get_block(blockpos)
                itemstack = mcpython.common.container.ItemStack.ItemStack(
                    block.NAME if type(block) != str else block
                )
                block = chunk.get_block(blockpos)
                if block:
                    block.on_request_item_for_block(itemstack)
                selected_slot = player.get_active_inventory_slot()

                for inventory, reverse in player.inventory_order:
                    slots: list = inventory.slots
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

    def _update(self, dt: float):
        """Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        player = shared.world.get_active_player()
        speed = mcpython.common.config.SPEED_DICT[player.gamemode][
            (0 if not shared.window.keys[key.LSHIFT] else 1)
            + (0 if not shared.world.get_active_player().flying else 2)
        ]

        if not shared.world.get_active_player().flying and shared.window.dy == 0:
            x, y, z = mcpython.util.math.normalize(player.position)
            block_inst = shared.world.get_active_dimension().get_block((x, y - 2, z))
            if (
                block_inst is not None
                and type(block_inst) != str
                and block_inst.CUSTOM_WALING_SPEED_MULTIPLIER is not None
            ):
                speed *= block_inst.CUSTOM_WALING_SPEED_MULTIPLIER

        if player.gamemode in (0, 2) and shared.window.keys[key.LSHIFT]:
            player.hunger -= dt * 0.2

        d = dt * speed  # distance covered this tick.
        dx, dy, dz = shared.window.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d

        # gravity
        if not shared.world.get_active_player().flying:
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

        # collisions
        x, y, z = player.position
        before = mcpython.util.math.position_to_chunk(player.position)
        if player.gamemode != 3:
            x, y, z = shared.window.collide(
                (x + dx, y + dy, z + dz), 2, player.position
            )
        else:
            x, y, z = x + dx, y + dy, z + dz
        if shared.window.dy < 0 and player.fallen_since_y is None:
            player.fallen_since_y = player.position[1]
        player.position = (x, y, z)
        if y < -10 and time.time() - self.void_damage_cooldown > 0.25:
            player.damage(1, check_gamemode=False)
            self.void_damage_cooldown = time.time()

        after = mcpython.util.math.position_to_chunk(player.position)
        if before != after:
            shared.world.change_chunks(before, after)

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

        if player.gamemode in (0, 2) and shared.world.get_active_dimension().get_block(
            (nx, ny, nz)
        ):
            player.damage(dt)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        player = shared.world.get_active_player()
        if not self.activate_mouse:
            return
        slot = player.get_active_inventory_slot()
        vector = shared.window.get_sight_vector()
        blockpos, previous, hitpos = shared.world.hit_test(player.position, vector)
        block = (
            shared.world.get_active_dimension().get_block(blockpos)
            if blockpos
            else None
        )
        cancel = False
        if not slot.get_itemstack().is_empty():
            if slot.get_itemstack().item.on_player_interact(
                player, block, button, modifiers
            ):
                cancel = True
        if block and type(block) != str:
            if not cancel and block.on_player_interaction(
                player, button, modifiers, hitpos
            ):
                cancel = True
        if cancel:
            self.set_cooldown = time.time()
            shared.window.mouse_pressing[button] = False
        else:
            self.calculate_new_break_time()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if shared.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y, _ = shared.world.get_active_player().rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            shared.world.get_active_player().rotation = (x, y, 0)
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_key_press(self, symbol: int, modifiers: int):
        if not self.activate_keyboard:
            return

        # does an hotkey override this key?
        for hotkey in self.active_hotkeys:
            if hotkey.blocks(symbol, modifiers):
                return

        if symbol == key.W and not shared.window.keys[key.S]:
            shared.window.strafe[0] = -1
        elif symbol == key.S and not shared.window.keys[key.W]:
            shared.window.strafe[0] = 1
        elif symbol == key.A and not shared.window.keys[key.D]:
            shared.window.strafe[1] = -1
        elif symbol == key.D and not shared.window.keys[key.A]:
            shared.window.strafe[1] = 1
        elif (
            symbol == key.SPACE
            and shared.world.get_active_player().inventory_chat
            not in shared.inventory_handler.opened_inventory_stack
        ):
            if (
                self.double_space_cooldown
                and time.time() - self.double_space_cooldown < 0.5
                and shared.world.get_active_player().gamemode == 1
            ):
                shared.world.get_active_player().flying = (
                    not shared.world.get_active_player().flying
                )
                self.double_space_cooldown = None
            else:
                if shared.window.dy == 0:
                    shared.window.dy = JUMP_SPEED
        elif (
            symbol in shared.window.num_keys
            and shared.world.get_active_player().gamemode in (0, 1)
            and not modifiers & key.MOD_SHIFT
        ):
            index = symbol - shared.window.num_keys[0]
            shared.world.get_active_player().set_active_inventory_slot(index)
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_key_release(self, symbol: int, modifiers: int):
        if not self.activate_keyboard:
            return

        # todo: make this configurable
        if symbol == key.W:
            shared.window.strafe[0] = 0 if not shared.window.keys[key.S] else 1
        elif symbol == key.S:
            shared.window.strafe[0] = 0 if not shared.window.keys[key.W] else -1
        elif symbol == key.A:
            shared.window.strafe[1] = 0 if not shared.window.keys[key.D] else 1
        elif symbol == key.D:
            shared.window.strafe[1] = 0 if not shared.window.keys[key.A] else -1
        elif symbol == key.SPACE:
            self.double_space_cooldown = time.time()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if self.activate_mouse and shared.window.exclusive:
            shared.world.get_active_player().active_inventory_slot -= scroll_y
            shared.world.get_active_player().active_inventory_slot = round(
                abs(shared.world.get_active_player().active_inventory_slot % 9)
            )
            if shared.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_draw_3d(self):
        pyglet.gl.glClearColor(*self.clear_color)
        pyglet.gl.glColor3d(*self.color_3d)

        if self.activate_3d_draw:
            shared.world.get_active_dimension().draw()
            if (
                self.activate_focused_block_draw
                and shared.world.get_active_player().gamemode != 3
            ):
                shared.window.draw_focused_block()

    def on_draw_2d(self):
        if self.active_lable:
            shared.window.draw_label()

        if self.activate_crosshair:
            shared.window.draw_reticle()
