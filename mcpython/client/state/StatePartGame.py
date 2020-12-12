"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from . import StatePart
from mcpython import shared as G
from mcpython.common.config import FLYING_SPEED, GRAVITY, TERMINAL_VELOCITY, JUMP_SPEED
from pyglet.window import key, mouse
import pyglet
import mcpython.common.container.ItemStack
import mcpython.common.config
import mcpython.util.math
import time
import mcpython.common.item.ItemFood as ItemFood
import mcpython.common.item.ItemTool as ItemTool
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
        status = all([G.window.keys[symbol] for symbol in self.keys])
        if self.active and not status:
            self.active = False
            if time.time() - self.press_start < self.min_press:
                return
            G.event_handler.call(self.event)
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
        vector = G.window.get_sight_vector()
        blockpos = G.world.hit_test(G.world.get_active_player().position, vector)[0]
        block = G.world.get_active_dimension().get_block(blockpos) if blockpos else None
        if not block:
            cls.break_time = None  # no break time because no block
        else:
            hardness = block.HARDNESS
            itemstack = (
                G.world.get_active_player()
                .get_active_inventory_slot()
                .get_itemstack()
                .copy()
            )
            istool = not itemstack.is_empty() and issubclass(
                type(itemstack.item), ItemTool.ItemTool
            )
            toollevel = itemstack.item.TOOL_LEVEL if istool else 0
            if not istool or not any(
                [x in block.BEST_TOOLS_TO_BREAK for x in itemstack.item.TOOL_TYPE]
            ):
                cls.break_time = (
                    1.5 if block.MINIMUM_TOOL_LEVEL <= toollevel else 5
                ) * hardness
            else:
                cls.break_time = (
                    (1.5 if block.MINIMUM_TOOL_LEVEL <= toollevel else 5)
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
                G.window.mouse_pressing.__setitem__(x, False)
                for x in G.window.mouse_pressing.keys()
            ]
        else:
            G.world.get_active_player().reset_moving_slot()

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

    def on_update(self, dt):
        for hotkey in self.active_hotkeys:
            hotkey.check()

        # do counting stuff  todo: change to per-mouse-button
        if any(G.window.mouse_pressing.values()):
            self.mouse_press_time += dt

        if (
            G.window.exclusive
            and any(G.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(
                G.world.get_active_player().position, vector
            )
            if blockpos:
                if (
                    blockpos != self.block_looking_at
                ):  # have we changed the block we were looking at?
                    self.block_looking_at = blockpos
                    self.mouse_press_time = 0

            if not self.break_time:
                self.calculate_new_break_time()

    def on_physics_update(self, dt):
        if not self.activate_physics:
            return
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)

    def on_left_click_interaction_update(self, dt):
        player = G.world.get_active_player()
        if (
            G.window.exclusive
            and any(G.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(player.position, vector)
            if (
                G.window.mouse_pressing[mouse.LEFT]
                and blockpos
                and G.world.get_active_dimension().get_block(blockpos)
            ):
                block = G.world.get_active_dimension().get_block(blockpos)
                chunk = G.world.get_active_dimension().get_chunk(
                    *mcpython.util.math.positionToChunk(blockpos)
                )
                if player.gamemode == 1:
                    if self.mouse_press_time >= 0.10:
                        chunk.remove_block(blockpos)
                        chunk.on_block_updated(blockpos)
                        chunk.check_neighbors(blockpos)
                elif player.gamemode == 0:
                    if (
                        type(block) != str
                        and self.mouse_press_time >= self.break_time
                        and block.IS_BREAKABLE
                    ):
                        if G.world.gamerulehandler.table["doTileDrops"].status.status:
                            items = G.loot_table_handler.get_drop_for_block(
                                block, player=player
                            )
                            if block:
                                [
                                    block.on_request_item_for_block(itemstack)
                                    for itemstack in items
                                ]
                            player.pick_up(items)
                        chunk.remove_block(blockpos)
                        chunk.on_block_updated(blockpos)
                        chunk.check_neighbors(blockpos)
                # todo: check if breakable in gamemode 2 by comparing item holders

    def on_right_click_interaction_update(self, dt):
        player = G.world.get_active_player()
        if (
            G.window.exclusive
            and any(G.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            if player.get_active_inventory_slot().get_itemstack().item and issubclass(
                type(player.get_active_inventory_slot().get_itemstack().item),
                ItemFood.ItemFood,
            ):
                itemfood = player.get_active_inventory_slot().get_itemstack().item
                if itemfood.on_eat():
                    self.set_cooldown = time.time() - 1
                    player.get_active_inventory_slot().get_itemstack().add_amount(-1)
                    if player.get_active_inventory_slot().get_itemstack().amount == 0:
                        player.get_active_inventory_slot().get_itemstack().clean()
                    return
            vector = G.window.get_sight_vector()
            blockpos, previous, hit_position = G.world.hit_test(player.position, vector)
            if blockpos:
                if G.window.mouse_pressing[mouse.RIGHT] and previous:
                    slot = player.get_active_inventory_slot()
                    if (
                        slot.get_itemstack().item
                        and slot.get_itemstack().item.HAS_BLOCK
                        and self.mouse_press_time > 0.10
                        and player.gamemode in (0, 1)
                    ):
                        x, y, z = previous
                        px, _, pz = mcpython.util.math.normalize(player.position)
                        py = math.ceil(player.position[1])
                        if not (
                            x == px and z == pz and py - 1 <= y <= py
                        ) and not G.world.get_active_dimension().get_block(previous):
                            chunk = (
                                G.world.get_active_dimension().get_chunk_for_position(
                                    previous
                                )
                            )
                            chunk.add_block(
                                previous,
                                slot.get_itemstack().item.get_block(),
                                lazy_setup=lambda block: block.set_creation_properties(
                                    set_to=blockpos,
                                    real_hit=hit_position,
                                    player=player,
                                ),
                            )
                            chunk.on_block_updated(previous)
                            slot.get_itemstack().item.on_set_from_item(
                                chunk.get_block(previous)
                            )
                            if player.gamemode == 0:
                                slot.get_itemstack().add_amount(-1)
                            self.mouse_press_time = 0
                            # todo: check if set-able in gamemode 2

    def on_middle_click_interaction_update(self, dt):
        player = G.world.get_active_player()
        if (
            G.window.exclusive
            and any(G.window.mouse_pressing.values())
            and time.time() - self.set_cooldown > 1
        ):
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(player.position, vector)
            if (
                G.window.mouse_pressing[mouse.MIDDLE]
                and blockpos
                and self.mouse_press_time > 0.1
            ):
                chunk = G.world.get_active_dimension().get_chunk_for_position(blockpos)
                self.mouse_press_time = 0
                block = G.world.get_active_dimension().get_block(blockpos)
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
                    player.pick_up(old_itemstack)
                    if G.window.mouse_pressing[mouse.LEFT]:
                        self.calculate_new_break_time()

    def _update(self, dt):
        """Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        player = G.world.get_active_player()
        speed = mcpython.common.config.SPEED_DICT[player.gamemode][
            (0 if not G.window.keys[key.LSHIFT] else 1)
            + (0 if not G.world.get_active_player().flying else 2)
        ]
        if not G.world.get_active_player().flying and G.window.dy == 0:
            x, y, z = mcpython.util.math.normalize(player.position)
            block_inst = G.world.get_active_dimension().get_block((x, y - 2, z))
            if (
                block_inst is not None
                and type(block_inst) != str
                and block_inst.CUSTOM_WALING_SPEED_MULTIPLIER is not None
            ):
                speed *= block_inst.CUSTOM_WALING_SPEED_MULTIPLIER
        if player.gamemode in (0, 2) and G.window.keys[key.LSHIFT]:
            player.hunger -= dt * 0.2
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = G.window.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not G.world.get_active_player().flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            G.window.dy -= dt * GRAVITY
            G.window.dy = max(G.window.dy, -TERMINAL_VELOCITY)
            dy += G.window.dy * dt
        elif self.activate_keyboard and not (
            G.window.keys[key.SPACE] and G.window.keys[key.LSHIFT]
        ):
            dy = (
                dt * 6
                if G.window.keys[key.SPACE]
                else (-dt * 6 if G.window.keys[key.LSHIFT] else 0)
            )
        # collisions
        x, y, z = player.position
        before = mcpython.util.math.positionToChunk(player.position)
        if player.gamemode != 3:
            x, y, z = G.window.collide((x + dx, y + dy, z + dz), 2, player.position)
        else:
            x, y, z = x + dx, y + dy, z + dz
        if G.window.dy < 0 and player.fallen_since_y is None:
            player.fallen_since_y = player.position[1]
        player.position = (x, y, z)
        if y < -10 and time.time() - self.void_damage_cooldown > 0.25:
            player.damage(1, check_gamemode=False)
            self.void_damage_cooldown = time.time()

        after = mcpython.util.math.positionToChunk(player.position)
        if before != after:
            G.world.change_chunks(before, after)

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

        if player.gamemode in (0, 2) and G.world.get_active_dimension().get_block(
            (nx, ny, nz)
        ):
            player.damage(dt)

    def on_mouse_press(self, x, y, button, modifiers):
        player = G.world.get_active_player()
        if not self.activate_mouse:
            return
        slot = player.get_active_inventory_slot()
        vector = G.window.get_sight_vector()
        blockpos, previous, hitpos = G.world.hit_test(player.position, vector)
        block = G.world.get_active_dimension().get_block(blockpos) if blockpos else None
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
            G.window.mouse_pressing[button] = False
        else:
            self.calculate_new_break_time()

    def on_mouse_motion(self, x, y, dx, dy):
        if G.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y, _ = G.world.get_active_player().rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            G.world.get_active_player().rotation = (x, y, 0)
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_key_press(self, symbol, modifiers):
        if not self.activate_keyboard:
            return

        # does an hotkey override this key?
        for hotkey in self.active_hotkeys:
            if hotkey.blocks(symbol, modifiers):
                return

        if symbol == key.W and not G.window.keys[key.S]:
            G.window.strafe[0] = -1
        elif symbol == key.S and not G.window.keys[key.W]:
            G.window.strafe[0] = 1
        elif symbol == key.A and not G.window.keys[key.D]:
            G.window.strafe[1] = -1
        elif symbol == key.D and not G.window.keys[key.A]:
            G.window.strafe[1] = 1
        elif (
            symbol == key.SPACE
            and G.world.get_active_player().inventory_chat
            not in G.inventory_handler.opened_inventorystack
        ):
            if (
                self.double_space_cooldown
                and time.time() - self.double_space_cooldown < 0.5
                and G.world.get_active_player().gamemode == 1
            ):
                G.world.get_active_player().flying = (
                    not G.world.get_active_player().flying
                )
                self.double_space_cooldown = None
            else:
                if G.window.dy == 0:
                    G.window.dy = JUMP_SPEED
        elif (
            symbol in G.window.num_keys
            and G.world.get_active_player().gamemode in (0, 1)
            and not modifiers & key.MOD_SHIFT
        ):
            index = symbol - G.window.num_keys[0]
            G.world.get_active_player().set_active_inventory_slot(index)
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_key_release(self, symbol, modifiers):
        if not self.activate_keyboard:
            return
        if symbol == key.W:
            G.window.strafe[0] = 0 if not G.window.keys[key.S] else 1
        elif symbol == key.S:
            G.window.strafe[0] = 0 if not G.window.keys[key.W] else -1
        elif symbol == key.A:
            G.window.strafe[1] = 0 if not G.window.keys[key.D] else 1
        elif symbol == key.D:
            G.window.strafe[1] = 0 if not G.window.keys[key.A] else -1
        elif symbol == key.SPACE:
            self.double_space_cooldown = time.time()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.activate_mouse and G.window.exclusive:
            G.world.get_active_player().active_inventory_slot -= scroll_y
            G.world.get_active_player().active_inventory_slot = round(
                abs(G.world.get_active_player().active_inventory_slot % 9)
            )
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_break_time()

    def on_draw_3d(self):
        pyglet.gl.glClearColor(*self.clear_color)
        pyglet.gl.glColor3d(*self.color_3d)
        if self.activate_3d_draw:
            G.world.get_active_dimension().draw()
            if (
                self.activate_focused_block_draw
                and G.world.get_active_player().gamemode != 3
            ):
                G.window.draw_focused_block()

    def on_draw_2d(self):
        if self.active_lable:
            G.window.draw_label()
        if self.activate_crosshair:
            G.window.draw_reticle()
