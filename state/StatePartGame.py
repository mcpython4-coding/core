"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
from . import StatePart
import globals as G
from config import FLYING_SPEED, WALKING_SPEED, GRAVITY, TERMINAL_VELOCITY, PLAYER_HEIGHT, JUMP_SPEED
from pyglet.window import key, mouse
import pyglet


class StatePartGame(StatePart.StatePart):
    def __init__(self, activate_physics=True, activate_mouse=True, activate_keyboard=True, activate_3d_draw=True,
                 activate_focused_block=True, glcolor3d=(1., 1., 1.)):
        self.activate_physics = activate_physics
        self.activate_mouse = activate_mouse
        self.activate_keyboard = activate_keyboard
        self.activate_3d_draw = activate_3d_draw
        self.activate_focused_block_draw = activate_focused_block
        self.glcolor3d = glcolor3d

        self.event_functions = [("gameloop:tick:end", self.on_update),
                                ("user:mouse:press", self.on_mouse_press),
                                ("user:mouse:motion", self.on_mouse_motion),
                                ("user:keyboard:press", self.on_key_press),
                                ("user:keyboard:release", self.on_key_release),
                                ("render:draw:3d", self.on_draw_3d),
                                ("render:draw:2d", self.on_draw_2d)]

    def activate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.activate_to_callback(eventname, function)

    def deactivate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.deactivate_from_callback(eventname, function)

    @G.eventhandler("gameloop:tick:end", callactive=False)
    def on_update(self, dt):
        if self.activate_physics:
            m = 8
            dt = min(dt, 0.2)
            for _ in range(m):
                self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if G.window.flying else WALKING_SPEED
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
        # collisions
        x, y, z = G.window.position
        if G.player.gamemode != 3: x, y, z = G.window.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        G.window.position = (x, y, z)

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.activate_mouse: return
        if G.window.exclusive:
            vector = G.window.get_sight_vector()
            blockpos, previous = G.window.model.hit_test(G.window.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous and G.player.gamemode in [0, 1]:
                    G.window.model.add_block(previous, G.window.block)
            elif button == mouse.LEFT and blockpos:
                block = G.window.model.world[blockpos]
                if block.is_brakeable() and G.player.gamemode in [0, 1]:
                    G.window.model.remove_block(blockpos)

    @G.eventhandler("user:mouse:motion", callactive=False)
    def on_mouse_motion(self, x, y, dx, dy):
        if G.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y = G.window.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            G.window.rotation = (x, y)

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if not self.activate_keyboard: return
        if symbol == key.W:
            G.window.strafe[0] -= 1
        elif symbol == key.S:
            G.window.strafe[0] += 1
        elif symbol == key.A:
            G.window.strafe[1] -= 1
        elif symbol == key.D:
            G.window.strafe[1] += 1
        elif symbol == key.SPACE:
            if G.window.dy == 0:
                G.window.dy = JUMP_SPEED
        elif symbol == key.TAB and G.player.gamemode == 1:
            G.window.flying = not G.window.flying
        elif symbol in G.window.num_keys and G.player.gamemode in (0, 1):
            index = (symbol - G.window.num_keys[0]) % len(G.window.inventory)
            G.window.block = G.window.inventory[index]

    @G.eventhandler("user:keyboard:release", callactive=False)
    def on_key_release(self, symbol, modifiers):
        if not self.activate_keyboard: return
        if symbol == key.W:
            G.window.strafe[0] += 1
        elif symbol == key.S:
            G.window.strafe[0] -= 1
        elif symbol == key.A:
            G.window.strafe[1] += 1
        elif symbol == key.D:
            G.window.strafe[1] -= 1

    @G.eventhandler("render:draw:3d", callactive=False)
    def on_draw_3d(self):
        pyglet.gl.glClearColor(0.5, 0.69, 1.0, 1)
        pyglet.gl.glColor3d(*self.glcolor3d)
        if self.activate_3d_draw:
            G.window.model.batch.draw()
            if self.activate_focused_block_draw:
                G.window.draw_focused_block()

    @G.eventhandler("render:draw:2d", callactive=False)
    def on_draw_2d(self):
        G.window.draw_label()
        G.window.draw_reticle()

