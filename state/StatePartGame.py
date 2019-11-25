"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import StatePart
import globals as G
from config import FLYING_SPEED, WALKING_SPEED, GRAVITY, TERMINAL_VELOCITY, PLAYER_HEIGHT, JUMP_SPEED
from pyglet.window import key, mouse
import pyglet
import gui.ItemStack
import config
import util.math
import time
import item.ItemFood as ItemFood
import item.ItemTool as ItemTool
import math


class StatePartGame(StatePart.StatePart):
    mouse_press_time = 0
    block_looking_at = None
    double_space_cooldown = 0
    set_cooldown = 0
    void_damage_cooldown = 0
    regenerate_cooldown = 0
    hunger_heart_cooldown = 0
    braketime = None

    @classmethod
    def calculate_new_braketime(cls):
        vector = G.window.get_sight_vector()
        blockpos = G.world.hit_test(G.window.position, vector)[0]
        block = G.world.get_active_dimension().get_block(blockpos) if blockpos else None
        if not block:
            cls.braketime = None  # no braketime because no block
        else:
            hardness = block.get_hardness()
            itemstack = G.player.get_active_inventory_slot().itemstack
            istool = itemstack.item and issubclass(type(itemstack.item), ItemTool.ItemTool)
            toollevel = itemstack.item.get_tool_level() if istool else 0
            if not istool or not any([x in block.get_best_tools() for x in itemstack.item.get_tool_type()]):
                cls.braketime = (1.5 if block.get_minimum_tool_level() <= toollevel else 5) * hardness
            else:
                cls.braketime = (1.5 if block.get_minimum_tool_level() <= toollevel else 5) * hardness / \
                                itemstack.item.get_speed_multiplyer()
            # todo: add factor when not on ground, when in water (when its added)

    def __init__(self, activate_physics=True, activate_mouse=True, activate_keyboard=True, activate_3d_draw=True,
                 activate_focused_block=True, glcolor3d=(1., 1., 1.), activate_crosshair=True, activate_lable=True,
                 clearcolor=(0.5, 0.69, 1.0, 1)):
        super().__init__()
        self.activate_physics = activate_physics
        self.activate_mouse = activate_mouse
        self.activate_keyboard = activate_keyboard
        self.activate_3d_draw = activate_3d_draw
        self.activate_focused_block_draw = activate_focused_block
        self.activate_crosshair = activate_crosshair
        self.active_lable = activate_lable
        self.glcolor3d = glcolor3d
        self.clearcolor = clearcolor

    def bind_to_eventbus(self):
        state = self.master[0]
        state.eventbus.subscribe("gameloop:tick:end", self.on_update)
        state.eventbus.subscribe("gameloop:tick:end", self.on_physics_update)
        state.eventbus.subscribe("gameloop:tick:end", self.on_left_click_interaction_update)
        state.eventbus.subscribe("gameloop:tick:end", self.on_right_click_interaction_update)
        state.eventbus.subscribe("gameloop:tick:end", self.on_middle_click_interaction_update)
        state.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        state.eventbus.subscribe("user:mouse:motion", self.on_mouse_motion)
        state.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        state.eventbus.subscribe("user:keyboard:release", self.on_key_release)
        state.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)
        state.eventbus.subscribe("render:draw:3d", self.on_draw_3d)
        state.eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def on_update(self, dt):
        # do counting stuff
        if any(G.window.mouse_pressing.values()):
            self.mouse_press_time += dt

        if G.window.exclusive and any(G.window.mouse_pressing.values()) and time.time() - self.set_cooldown > 1:
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(G.window.position, vector)
            if blockpos:
                if blockpos != self.block_looking_at:  # have we changed the block we were looking at?
                    self.block_looking_at = blockpos
                    self.mouse_press_time = 0

            if not self.braketime:
                self.calculate_new_braketime()

    def on_physics_update(self, dt):
        if not self.activate_physics: return
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)

    def on_left_click_interaction_update(self, dt):
        if G.window.exclusive and any(G.window.mouse_pressing.values()) and time.time() - self.set_cooldown > 1:
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(G.window.position, vector)
            if G.window.mouse_pressing[mouse.LEFT] and blockpos and G.world.get_active_dimension().get_block(blockpos):
                block = G.world.get_active_dimension().get_block(blockpos)
                chunk = G.world.get_active_dimension().get_chunk(*util.math.sectorize(blockpos))
                if G.player.gamemode == 1:
                    if self.mouse_press_time >= 0.10:
                        chunk.remove_block(blockpos)
                        chunk.check_neighbors(blockpos)
                elif G.player.gamemode == 0:
                    if self.mouse_press_time >= self.braketime:
                        itemstack = gui.ItemStack.ItemStack(block.get_name() if type(block) != str else block)
                        block = chunk.get_block(blockpos)
                        if block: block.on_request_item_for_block(itemstack)
                        G.player.add_to_free_place(itemstack)
                        chunk.remove_block(blockpos)
                        chunk.check_neighbors(blockpos)
                # todo: check if breakable in gamemode 2

    def on_right_click_interaction_update(self, dt):
        if G.window.exclusive and any(G.window.mouse_pressing.values()) and time.time() - self.set_cooldown > 1:
            if G.player.get_active_inventory_slot().itemstack.item and \
                    issubclass(type(G.player.get_active_inventory_slot().itemstack.item), ItemFood.ItemFood):
                itemfood = G.player.get_active_inventory_slot().itemstack.item
                if itemfood.on_eat():
                    self.set_cooldown = time.time() - 1
                    G.player.get_active_inventory_slot().itemstack.amount -= 1
                    if G.player.get_active_inventory_slot().itemstack.amount == 0:
                        G.player.get_active_inventory_slot().itemstack.clean()
                    return
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(G.window.position, vector)
            if blockpos:
                if G.window.mouse_pressing[mouse.RIGHT] and previous:
                    slot = G.player.get_active_inventory_slot()
                    if slot.itemstack.item and slot.itemstack.item.has_block() and self.mouse_press_time > 0.12 and \
                            G.player.gamemode in (0, 1):
                        x, y, z = previous
                        px, _, pz = util.math.normalize(G.window.position)
                        py = math.ceil(G.window.position[1])
                        if not (x == px and z == pz and py-1 <= y <= py) and not G.world.get_active_dimension().\
                                get_block(previous):
                            G.world.get_active_dimension().add_block(
                                previous, slot.itemstack.item.get_block(), kwargs={"set_to": blockpos,
                                                                                   "real_hit": hitpos})
                            slot.itemstack.item.on_set_from_item(G.world.get_active_dimension().get_block(previous))
                            if G.player.gamemode == 0:
                                slot.itemstack.amount -= 1
                                if slot.itemstack.amount == 0:
                                    slot.itemstack.clean()
                            self.mouse_press_time = 0
                            # todo: check if setable in gamemode 2

    def on_middle_click_interaction_update(self, dt):
        if G.window.exclusive and any(G.window.mouse_pressing.values()) and time.time() - self.set_cooldown > 1:
            vector = G.window.get_sight_vector()
            blockpos, previous, hitpos = G.world.hit_test(G.window.position, vector)
            if G.window.mouse_pressing[mouse.MIDDLE] and blockpos and self.mouse_press_time > 0.1:
                chunk = G.world.get_active_dimension().get_chunk_for_position(blockpos)
                self.mouse_press_time = 0
                block = G.world.get_active_dimension().get_block(blockpos)
                itemstack = gui.ItemStack.ItemStack(block.get_name() if type(block) != str else block)
                block = chunk.get_block(blockpos)
                if block: block.on_request_item_for_block(itemstack)
                G.player.add_to_free_place(itemstack)
                selected_slot = G.player.get_active_inventory_slot()
                for inventoryname, reverse in G.player.inventory_order:
                    inventory = G.player.inventorys[inventoryname]
                    slots: list = inventory.slots
                    if reverse:
                        slots.reverse()
                    for slot in slots:
                        if slot.itemstack.item and slot.itemstack.item.has_block() and \
                                slot.itemstack.item == itemstack.item:
                            if inventoryname != "hotbar":
                                selected_slot.itemstack, slot.itemstack = slot.itemstack, selected_slot.itemstack
                            else:
                                G.player.set_active_inventory_slot(slots.index(slot))
                            return
                if G.player.gamemode == 1:
                    old_itemstack = selected_slot.itemstack
                    selected_slot.itemstack = itemstack
                    G.player.add_to_free_place(old_itemstack)
                    if G.window.mouse_pressing[mouse.LEFT]: self.calculate_new_braketime()

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        speed = config.SPEED_DICT[G.player.gamemode][(0 if not G.window.keys[key.LSHIFT] else 1) +
                                                     (0 if not G.window.flying else 2)]
        if G.player.gamemode in (0, 2) and G.window.keys[key.LSHIFT]:
            G.player.hunger -= dt*0.2
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = G.window.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not G.window.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            G.window.dy -= dt * GRAVITY
            G.window.dy = max(G.window.dy, -TERMINAL_VELOCITY)
            dy += G.window.dy * dt
        elif self.activate_keyboard and not (G.window.keys[key.SPACE] and G.window.keys[key.LSHIFT]):
            dy = dt*6 if G.window.keys[key.SPACE] else (-dt*6 if G.window.keys[key.LSHIFT] else 0)
        # collisions
        x, y, z = G.window.position
        if G.player.gamemode != 3:
            x, y, z = G.window.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        else:
            x, y, z = x + dx, y + dy, z + dz
        if G.window.dy < 0 and G.player.fallen_since_y is None:
            G.player.fallen_since_y = G.window.position[1]
        G.window.position = (x, y, z)
        if y < -10 and time.time() - self.void_damage_cooldown > 0.25:
            G.player.damage(1, check_gamemode=False)
            self.void_damage_cooldown = time.time()

        if G.player.hearts < 20 and G.player.hunger > 4 and time.time() - self.regenerate_cooldown > 2 and \
                G.player.gamemode in (0, 2):
            G.player.hearts += 1
            G.player.hunger -= 0.5
            self.regenerate_cooldown = time.time()

        if G.player.hunger == 0 and time.time() - self.hunger_heart_cooldown > 1:
            G.player.damage(1)
            self.hunger_heart_cooldown = time.time()

        nx, _, nz = util.math.normalize(G.window.position)
        ny = math.ceil(G.window.position[1])

        if G.player.gamemode in (0, 2) and G.world.get_active_dimension().get_block((nx, ny, nz)):
            G.player.damage(dt)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.activate_mouse: return
        slot = G.player.get_active_inventory_slot()
        vector = G.window.get_sight_vector()
        blockpos, previous, hitpos = G.world.hit_test(G.window.position, vector)
        block = G.world.get_active_dimension().get_block(blockpos) if blockpos else None
        cancel = False
        if not slot.itemstack.is_empty():
            if slot.itemstack.item.on_player_interact(block, button, modifiers):
                cancel = True
        if block and type(block) != str:
            if not cancel and block.on_player_interact(slot.itemstack, button, modifiers, hitpos):
                cancel = True
        if cancel:
            self.set_cooldown = time.time()
            G.window.mouse_pressing[button] = False
        else:
            self.calculate_new_braketime()

    def on_mouse_motion(self, x, y, dx, dy):
        if G.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y = G.window.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            G.window.rotation = (x, y)
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_braketime()

    def on_key_press(self, symbol, modifiers):
        if not self.activate_keyboard: return
        if symbol == key.W and not G.window.keys[key.S]:
            G.window.strafe[0] = -1
        elif symbol == key.S and not G.window.keys[key.W]:
            G.window.strafe[0] = 1
        elif symbol == key.A and not G.window.keys[key.D]:
            G.window.strafe[1] = -1
        elif symbol == key.D and not G.window.keys[key.A]:
            G.window.strafe[1] = 1
        elif symbol == key.SPACE and G.player.inventorys["chat"] not in G.inventoryhandler.opened_inventorystack:
            if self.double_space_cooldown and time.time() - self.double_space_cooldown < 0.5 and G.player.gamemode == 1:
                G.window.flying = not G.window.flying
                self.double_space_cooldown = None
            else:
                if G.window.dy == 0:
                    G.window.dy = JUMP_SPEED
        elif symbol in G.window.num_keys and G.player.gamemode in (0, 1) and not modifiers & key.MOD_SHIFT:
            index = symbol - G.window.num_keys[0]
            G.player.set_active_inventory_slot(index)
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_braketime()

    def on_key_release(self, symbol, modifiers):
        if not self.activate_keyboard: return
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
        if self.activate_mouse:
            G.player.active_inventory_slot -= scroll_y
            G.player.active_inventory_slot = round(abs(G.player.active_inventory_slot % 9))
            if G.window.mouse_pressing[mouse.LEFT]:
                self.calculate_new_braketime()

    def on_draw_3d(self):
        pyglet.gl.glClearColor(*self.clearcolor)
        pyglet.gl.glColor3d(*self.glcolor3d)
        if self.activate_3d_draw:
            G.world.get_active_dimension().draw()
            if self.activate_focused_block_draw and G.player.gamemode != 3:
                G.window.draw_focused_block()

    def on_draw_2d(self):
        if self.active_lable:
            G.window.draw_label()
        if self.activate_crosshair:
            G.window.draw_reticle()

