"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import sys

import PIL.Image
import psutil
import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
import cProfile

import mcpython.ResourceLocator
import mcpython.event.EventHandler
import mcpython.event.TickHandler
import mcpython.config
import mcpython.rendering.OpenGLSetupFile
import mcpython.state.StateHandler
import mcpython.state.StatePartGame
import mcpython.util.math
import mcpython.util.texture
from mcpython.config import *  # todo: remove
from mcpython.util.math import *  # todo: remove


class NoWindow:
    """
    class simulating an window for the no-window mode
    """

    def __init__(self, *args, **kwargs):
        self.width = self.height = 200

    def get_size(self):
        return self.width, self.height

    def push_handlers(self, handler):
        pass

    def close(self):
        pass

    def set_caption(self, caption: str):
        pass

    def set_icon(self, *args):
        pass


class Window(pyglet.window.Window if "--no-window" not in sys.argv else NoWindow):

    def __init__(self, *args, **kwargs):
        """
        creates an new window-instance
        :param args: args send to pyglet.window.Window-constructor
        :param kwargs: kwargs send to pyglet.window.Window-constructor
        """

        super(Window, self).__init__(*args, **kwargs)

        G.window = self  # write window instance to globals.py for sharing

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise. todo: move to player's movement-attribute
        self.strafe = [0, 0]

        # Which sector the player is currently in.
        self.sector = None  # todo: move to player

        # Velocity in the y (upward) direction.
        self.dy = 0  # todo: move to player

        # Convenience list of num keys, todo: move to config.py
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9]

        # Instance of the model that handles the world.  todo: remove attribute
        self.world = G.world

        # The label that is displayed in the top left of the canvas.  todo: move to separated class
        self.label = pyglet.text.Label('', font_name='Arial', font_size=10,
                                       x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
                                       color=(0, 0, 0, 255))
        self.label2 = pyglet.text.Label('', font_name='Arial', font_size=10,
                                        x=10, y=self.height - 22, anchor_x='left', anchor_y='top',
                                        color=(0, 0, 0, 255))
        self.label3 = pyglet.text.Label('', font_name='Arial', font_size=10,
                                        x=self.width - 10, y=self.height - 34, anchor_x='right', anchor_y='top',
                                        color=(0, 0, 0, 255))

        self.cpu_usage = psutil.cpu_percent(interval=None)  # todo: move to separated class
        self.cpu_usage_timer = 0  # todo: move to separated class

        # storing mouse information todo: use pyglet's mouse handler
        self.mouse_pressing = {mouse.LEFT: False, mouse.RIGHT: False, mouse.MIDDLE: False}
        self.mouse_position = (0, 0)

        self.draw_profiler = cProfile.Profile()  # todo: move to separated class
        self.tick_profiler = cProfile.Profile()  # todo: move to separated class

        # This call schedules the `update()` method to be called 20 times per sec. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 0.05)
        pyglet.clock.schedule_interval(self.print_profiler, 10)

        mcpython.state.StateHandler.load()  # load the state system

        self.keys = key.KeyStateHandler()  # key handler from pyglet
        self.push_handlers(self.keys)

        # todo: move to seperated class
        self.CROSSHAIRS_TEXTURE = mcpython.util.texture.to_pyglet_image(
            mcpython.ResourceLocator.read("gui/icons", "pil").crop((0, 0, 15, 15)).resize((30, 30), PIL.Image.NEAREST))

        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:game_crash", self.close)
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:copy_block_or_entity_data",
                                                               self.get_block_entity_info)

    @deprecation.deprecated("dev4-3", "a1.2.0")
    def get_flying(self): return G.world.get_active_player().is_flying

    @deprecation.deprecated("dev4-3", "a1.2.0")
    def set_flying(self, flying): G.world.get_active_player().is_flying = flying

    flying = property(get_flying, set_flying)

    def print_profiler(self, dt=None):
        """
        will print the enabled profiler(s)
        """
        if not mcpython.config.ENABLE_PROFILING: return

        if mcpython.config.ENABLE_PROFILER_DRAW:
            self.draw_profiler.print_stats(1)
            self.draw_profiler.clear()

        if mcpython.config.ENABLE_PROFILER_TICK:
            self.tick_profiler.print_stats(1)
            self.tick_profiler.clear()

    def reset_caption(self):
        """
        will set the caption of the window to the default one
        """
        self.set_caption("mcpython 4 - {}".format(mcpython.config.FULL_VERSION_NAME))

    def set_exclusive_mouse(self, exclusive):
        """
        If `exclusive` is True, the game will capture the mouse and not display it. Otherwise,
        the mouse is free to move
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    @classmethod
    def get_sight_vector(cls):
        """
        Returns the current line of sight vector indicating the direction
        the player is looking.
        todo: move to player
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

    def get_motion_vector(self) -> tuple:
        """
        Returns the current motion vector indicating the velocity of the
        player.
        :return: vector: Tuple containing the velocity in x, y, and z respectively.
        todo: integrate into player movement
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

    def update(self, dt: float):
        """
        This method is scheduled to be called repeatedly by the pyglet clock.
        :param dt: The change in time since the last call.
        """
        if mcpython.config.ENABLE_PROFILER_TICK and mcpython.config.ENABLE_PROFILING: self.tick_profiler.enable()
        G.eventhandler.call("gameloop:tick:start", dt)

        self.cpu_usage_timer += dt
        if self.cpu_usage_timer > mcpython.config.CPU_USAGE_REFRESH_TIME:
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.cpu_usage_timer = 0

        # todo: change to attribute in State-class
        if dt > 3 and G.statehandler.active_state.NAME not in ["minecraft:modloading"]:
            logger.println("[warning] running behind normal tick, did you overload game? missing " +
                           str(dt - 0.05) + " seconds")
        if any(type(x) == mcpython.state.StatePartGame.StatePartGame for x in G.statehandler.active_state.parts):
            G.worldgenerationhandler.task_handler.process_tasks(timer=0.02)
        sector = sectorize(G.world.get_active_player().position)
        if sector != self.sector:
            pyglet.clock.schedule_once(lambda _: G.world.change_chunks(self.sector, sector), 0.1)
            if self.sector is None:
                G.worldgenerationhandler.task_handler.process_tasks()
            self.sector = sector

        G.eventhandler.call("gameloop:tick:end", dt)
        if mcpython.config.ENABLE_PROFILER_TICK and mcpython.config.ENABLE_PROFILING: self.tick_profiler.disable()

    def collide(self, position, height):
        """
        Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        :param position: The (x, y, z) position to check for collisions at.
        :param height: The height of the player.
        :return The new position of the player taking into account collisions.
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
                    if not blockstate:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    if face == (0, -1, 0):
                        G.world.get_active_player().flying = False
                        if G.world.get_active_player().gamemode in (
                                0, 2) and G.world.get_active_player().fallen_since_y is not None:
                            dy = G.world.get_active_player().fallen_since_y - G.world.get_active_player().position[
                                1] - 3
                            if dy > 0 and G.world.gamerulehandler.table["fallDamage"].status.status:
                                G.world.get_active_player().damage(dy)
                            G.world.get_active_player().fallen_since_y = None
                    break
        return tuple(p)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when a mouse button is pressed. See pyglet docs for button amd modifier mappings.

        :param x, y: The coordinates of the mouse click. Always center of the screen if the mouse is captured.
        :param button: Number representing mouse button that was clicked. 1 = left button, 4 = right button.
            [access via pyglet.window.mouse]
        :param modifiers : Number representing any modifying keys that were pressed when the mouse button was clicked.
            [access via pyglet.window.key.MOD_[...]]
        """
        self.mouse_pressing[button] = True
        G.eventhandler.call("user:mouse:press", x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """
        called when an button is released with the same argument as on_mouse_press
        """
        self.mouse_pressing[button] = False
        G.eventhandler.call("user:mouse:release", x, y, button, modifiers)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        """
        called when the mouse moves over the screen while one or more buttons are pressed
        :param x: the new x position
        :param y: the new y position
        :param dx: the delta x
        :param dy: the delta y
        :param buttons: the buttons pressed
        :param modifiers: the modifiers pressed
        """
        self.mouse_position = (x, y)
        G.eventhandler.call("user:mouse:drag", x, y, dx, dy, buttons, modifiers)
        if self.exclusive:
            self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """
        called by pyglet when the mouse wheel is spinned
        :param x: the new x scroll
        :param y: the new y scroll
        :param scroll_x: the delta x
        :param scroll_y: the detla y
        """
        G.eventhandler.call("user:mouse:scroll", x, y, scroll_x, scroll_y)

    def on_mouse_motion(self, x: int, y: int, dx: float, dy: float):
        """
        Called when the player moves the mouse.

        :param x, y: The coordinates of the mouse click. Always center of the screen if the mouse is captured.
        :param dx, dy : The movement of the mouse.

        """
        G.eventhandler.call("user:mouse:motion", x, y, dx, dy)
        self.mouse_position = (x, y)

    def on_key_press(self, symbol: int, modifiers: int):
        """
        Called when the player presses a key. See pyglet docs for key mappings.
        :param symbol: Number representing the key that was pressed.
        :param modifiers: Number representing any modifying keys that were pressed.
        """
        G.eventhandler.call("user:keyboard:press", symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        """
        Called when the player releases a key. See pyglet docs for key mappings.
        :param symbol: Number representing the key that was pressed.
        :param modifiers: Number representing any modifying keys that were pressed.
        """
        G.eventhandler.call("user:keyboard:release", symbol, modifiers)

    def on_resize(self, width: int, height: int):
        """
        Called when the window is resized to a new `width` and `height`.
        """
        # labels todo: move to separated class
        self.label.y = height - 10
        self.label2.y = height - 22
        self.label3.x = width - 10
        self.label3.y = height - 34
        G.eventhandler.call("user:window:resize", width, height)

    def set_2d(self):
        width, height = self.get_size()
        viewport = self.get_viewport_size()
        mcpython.rendering.OpenGLSetupFile.execute_file_by_name("set_2d", width=max(1, width), height=max(1, height),
                                                                viewport_0=max(1, viewport[0]),
                                                                viewport_1=max(1, viewport[1]))
        # G.rendering_helper.setup2d()
        pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)

    def set_3d(self, position=None, rotation=None):
        if G.world.get_active_player() is None: return
        if G.rendering_helper.default_3d_stack is None:
            G.rendering_helper.default_3d_stack = G.rendering_helper.get_dynamic_3d_matrix_stack()
        G.rendering_helper.default_3d_stack.apply()
        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)

    def on_draw(self):
        """
        Called by pyglet to draw the canvas.
        """
        # make sure that the state of the rendering helper is saved for later usage
        status = G.rendering_helper.save_status(add_to_stack=False)

        # check for profiling
        if mcpython.config.ENABLE_PROFILER_DRAW and mcpython.config.ENABLE_PROFILING: self.draw_profiler.enable()

        G.eventhandler.call("render:draw:pre_clear")
        self.clear()  # clear the screen
        G.eventhandler.call("render:draw:pre_setup")
        self.set_2d()
        G.eventhandler.call("render:draw:2d:background_pre")
        self.set_3d()  # setup for 3d drawing
        G.eventhandler.call("render:draw:3d")  # call general 3d rendering event
        self.set_2d()  # setup for 2d rendering
        G.eventhandler.call("render:draw:2d:background")  # call pre 2d
        G.eventhandler.call("render:draw:2d")  # call normal 2d
        G.eventhandler.call("render:draw:2d:overlay")  # call overlay 2d
        if mcpython.config.ENABLE_PROFILER_DRAW and mcpython.config.ENABLE_PROFILING: self.draw_profiler.disable()
        G.rendering_helper.apply(status)
        G.eventhandler.call("render:draw:post:cleanup")

    def draw_focused_block(self):
        """
        Draw black edges around the block that is currently under the crosshairs.
        """
        vector = self.get_sight_vector()
        block = G.world.hit_test(G.world.get_active_player().position, vector)[0]
        if block:
            block = G.world.get_active_dimension().get_block(block)
            if block: block.get_view_bbox().draw_outline(block.position)

    def draw_label(self):
        """
        Draw the label in the top left of the screen.
        """
        x, y, z = G.world.get_active_player().position
        nx, ny, nz = mcpython.util.math.normalize(G.world.get_active_player().position)
        if not G.world.gamerulehandler.table["showCoordinates"].status.status:
            x = y = z = "?"
        chunk = G.world.get_active_dimension().get_chunk(*mcpython.util.math.sectorize(
            G.world.get_active_player().position), create=False)
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
                self.label.text += ", biome: " + str(biomemap[(nx, nz)])
        self.label.draw()
        process = psutil.Process()
        mem_info = process.memory_info()
        used_m = mem_info.rss
        total_m = psutil.virtual_memory().total
        with process.oneshot():
            self.label3.text = "CPU usage: {}%; Memory usage: {}MB/{}MB ({}%)".format(
                self.cpu_usage, used_m // 2 ** 20, total_m // 2 ** 20, round(used_m / total_m * 10000) / 100)
        self.label3.draw()

    def get_block_entity_info(self):
        """
        used by hotkey for copying entity data to the clipboard
        """
        import clipboard
        vector = self.get_sight_vector()
        blockpos, previous, hitpos = G.world.hit_test(G.world.get_active_player().position, vector)
        if blockpos:
            blockname = G.world.get_active_dimension().get_block(blockpos)
            if type(blockname) != str: blockname = blockname.NAME
            clipboard.copy(blockname)

    def draw_reticle(self):
        """
        Draw the crosshairs in the center of the screen.
        """
        pyglet.gl.glColor3d(255, 255, 255)
        wx, wy = self.get_size()
        self.CROSSHAIRS_TEXTURE.blit(wx // 2 - self.CROSSHAIRS_TEXTURE.width // 2,
                                     wy // 2 - self.CROSSHAIRS_TEXTURE.height // 2)

    def on_text(self, text: str):
        """
        called by pyglet with decoded key values when an text is entered
        :param text: the text entered
        """
        G.eventhandler.call("user:keyboard:enter", text)

    def on_close(self):
        """
        called when the window tries to close itself
        cleans up some stuff before closing
        """
        if G.world.savefile.save_in_progress: return
        if G.world.world_loaded:
            # have we an world which should be saved?
            G.world.get_active_player().inventories["main"].remove_items_from_crafting()
            G.world.savefile.save_world(override=True)
        self.set_fullscreen(False)
        self.close()
