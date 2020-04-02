"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import pyglet
from pyglet.gl import *
from config import *
from pyglet.window import key, mouse
from util.math import *
import time
import globals as G
import state.StateHandler
import util.math
import ResourceLocator
import util.texture
import logger
import PIL.Image
import psutil
import event.EventHandler
import event.TickHandler
import rendering.OpenGLSetupFile


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        G.window = self

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Which sector the player is currently in.
        self.sector = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        # Convenience list of num keys, todo: move to config.py
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9]

        # Instance of the model that handles the world.
        self.world = G.world

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=10,
                                       x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
                                       color=(0, 0, 0, 255))
        self.label2 = pyglet.text.Label('', font_name='Arial', font_size=10,
                                        x=10, y=self.height - 22, anchor_x='left', anchor_y='top',
                                        color=(0, 0, 0, 255))
        self.label3 = pyglet.text.Label('', font_name='Arial', font_size=10,
                                        x=self.width - 10, y=self.height - 34, anchor_x='right', anchor_y='top',
                                        color=(0, 0, 0, 255))

        self.cpu_usage = psutil.cpu_percent(interval=None)
        self.cpu_usage_timer = 0

        # storing mouse information
        self.mouse_pressing = {mouse.LEFT: False, mouse.RIGHT: False, mouse.MIDDLE: False}
        self.mouse_position = (0, 0)

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

        state.StateHandler.load()

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.CROSSHAIRS_TEXTURE = util.texture.to_pyglet_image(
            ResourceLocator.read("gui/icons", "pil").crop((0, 0, 15, 15)).resize((30, 30), PIL.Image.NEAREST))

        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:game_crash", self.close)
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:copy_block_or_entity_data", self.get_block_entity_info)

    def reset_caption(self):
        self.set_caption("mcpython 4 - {}".format(config.FULL_VERSION_NAME))

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y, _ = G.world.get_active_player().rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return dx, dy, dz

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y, _ = G.world.get_active_player().rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            dy = 0.0
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        G.eventhandler.call("gameloop:tick:start", dt)

        self.cpu_usage_timer += dt
        if self.cpu_usage_timer > config.CPU_USAGE_REFRESH_TIME:
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.cpu_usage_timer = 0

        # todo: change to attribute in State-class
        if dt > 3 and G.statehandler.active_state.NAME not in ["minecraft:modloading"]:
            logger.println("[warning] running behind normal tick, did you overload game? missing " +
                           str(dt - 1.0 / TICKS_PER_SEC)+" seconds")
        self.world.process_queue()
        sector = sectorize(G.world.get_active_player().position)
        if sector != self.sector:
            pyglet.clock.schedule_once(lambda _: G.world.change_sectors(self.sector, sector), 0.1)
            if self.sector is None:
                G.world.process_entire_queue()
            self.sector = sector

        G.eventhandler.call("gameloop:tick:end", dt)

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.1
        p = list(position)
        np = normalize(position)
        for face in ADVANCED_FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    chunk = G.world.get_active_dimension().get_chunk_for_position(tuple(op), generate=False)
                    blockstate = chunk.get_block(tuple(op)) is not None
                    if not chunk.generated:
                        if G.world.config["enable_world_barrier"]:
                            blockstate = True
                        # elif G.world.config["enable_auto_gen"] and not blockstate:
                        #     G.worldgenerationhandler.add_chunk_to_generation_list(chunk, prior=True)
                    if not blockstate:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    if face == (0, -1, 0):
                        G.window.flying = False
                        if G.world.get_active_player().gamemode in (0, 2) and G.world.get_active_player().fallen_since_y is not None:
                            dy = G.world.get_active_player().fallen_since_y - G.world.get_active_player().position[1] - 3
                            if dy > 0 and G.world.gamerulehandler.table["fallDamage"].status.status:
                                G.world.get_active_player().damage(dy)
                            G.world.get_active_player().fallen_since_y = None
                    # if not chunk.generated and G.world.config["enable_auto_gen"]:
                    #     G.worldgenerationhandler.add_chunk_to_generation_list(chunk, prior=True)
                    break
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        self.mouse_pressing[button] = True
        G.eventhandler.call("user:mouse:press", x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_pressing[button] = False
        G.eventhandler.call("user:mouse:release", x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_position = (x, y)
        G.eventhandler.call("user:mouse:drag", x, y, dx, dy, buttons, modifiers)
        if self.exclusive:
            self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        G.eventhandler.call("user:mouse:scroll", x, y, scroll_x, scroll_y)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        G.eventhandler.call("user:mouse:motion", x, y, dx, dy)
        self.mouse_position = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        G.eventhandler.call("user:keyboard:press", symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        G.eventhandler.call("user:keyboard:release", symbol, modifiers)

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # label
        self.label.y = height - 10
        self.label2.y = height - 22
        self.label3.x = width - 10
        self.label3.y = height - 34
        G.eventhandler.call("user:window:resize", width, height)

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        viewport = self.get_viewport_size()
        rendering.OpenGLSetupFile.execute_file_by_name("set_2d", width=max(1, width), height=max(1, height),
                                                       viewport_0=max(1, viewport[0]),
                                                       viewport_1=max(1, viewport[1]))

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        viewport = self.get_viewport_size()
        rotation = G.world.get_active_player().rotation
        position = G.world.get_active_player().position
        rendering.OpenGLSetupFile.execute_file_by_name("set_3d", width=width, height=height,
                                                       viewport_0=max(1, viewport[0]),
                                                       viewport_1=max(1, viewport[1]), rotation_x=rotation[0],
                                                       rotation_y=rotation[1], position_x=position[0],
                                                       position_y=position[1], position_z=position[2],
                                                       trans_rot_x=math.cos(math.radians(rotation[0])),
                                                       trans_rot_y=math.sin(math.radians(rotation[0])))

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        G.eventhandler.call("render:draw:3d")
        self.set_2d()
        G.eventhandler.call("render:draw:2d:background")
        G.eventhandler.call("render:draw:2d")
        G.eventhandler.call("render:draw:2d:overlay")

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = G.world.hit_test(G.world.get_active_player().position, vector)[0]
        if block:
            block = G.world.get_active_dimension().get_block(block)
            if block: block.get_view_bbox().draw_outline(block.position)

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = G.world.get_active_player().position
        nx, ny, nz = util.math.normalize(G.world.get_active_player().position)
        if not G.world.gamerulehandler.table["showCoordinates"].status.status:
            x = y = z = "?"
        chunk = G.world.get_active_dimension().get_chunk(*util.math.sectorize(G.world.get_active_player().position), create=False)
        self.label.text = '%02d (%.2f, %.2f, %.2f) [region %01d %01d], gamemode %01d' % (
            pyglet.clock.get_fps(), x, y, z, 0, 0, G.world.get_active_player().gamemode)
        vector = G.window.get_sight_vector()
        blockpos, previous, hitpos = G.world.hit_test(G.world.get_active_player().position, vector)
        if blockpos:
            blockname = G.world.get_active_dimension().get_block(blockpos)
            if type(blockname) != str: blockname = blockname.NAME
            self.label2.text = "looking at '{}(position={})'".format(
                blockname, blockpos if G.world.gamerulehandler.table["showCoordinates"].status.status else
                ("?", "?", "?"))
            self.label2.draw()
            self.label3.y = self.height - 34
        else:
            self.label3.y = self.height - 22
        if chunk:
            biomemap = chunk.get_value("biomemap")
            if (nx, nz) in biomemap:
                self.label.text += ", biome: "+str(biomemap[(nx, nz)])
        self.label.draw()
        process = psutil.Process()
        mem_info = process.memory_info()
        used_m = mem_info.rss
        total_m = psutil.virtual_memory().total
        with process.oneshot():
            self.label3.text = "CPU usage: {}%; Memory usage: {}MB/{}MB ({}%)".format(
                self.cpu_usage, used_m//2**20, total_m//2**20, round(used_m/total_m*10000)/100)
        self.label3.draw()

    def get_block_entity_info(self):
        import clipboard
        vector = self.get_sight_vector()
        blockpos, previous, hitpos = G.world.hit_test(G.world.get_active_player().position, vector)
        if blockpos:
            blockname = G.world.get_active_dimension().get_block(blockpos)
            if type(blockname) != str: blockname = blockname.NAME
            clipboard.copy(blockname)

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        pyglet.gl.glColor3d(255, 255, 255)
        wx, wy = self.get_size()
        self.CROSSHAIRS_TEXTURE.blit(wx//2-self.CROSSHAIRS_TEXTURE.width//2,
                                     wy//2-self.CROSSHAIRS_TEXTURE.height//2)

    def on_text(self, text):
        G.eventhandler.call("user:keyboard:enter", text)

    def on_close(self):
        if G.world.savefile.save_in_progress: return
        if G.statehandler.active_state is not None and any(
                [part.NAME == "minecraft:state_part_game" for part in G.statehandler.active_state.parts]):
            G.world.savefile.save_world(override=True)
        self.close()

