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
import asyncio
import cProfile
import time

import mcpython.common.config
import mcpython.common.event.TickHandler
import mcpython.common.state.GameViewStatePart
import mcpython.common.state.StateHandler
import mcpython.engine.event.EventHandler
import mcpython.engine.rendering.RenderingLayerManager
import mcpython.engine.rendering.util
import mcpython.engine.ResourceLoader
import mcpython.util.math
import mcpython.util.texture
import psutil
import pyglet
from bytecodemanipulation.OptimiserAnnotations import name_is_static
from mcpython.common.config import *  # todo: remove
from mcpython.util.annotation import onlyInClient
from mcpython.util.math import *  # todo: remove

if shared.IS_CLIENT:
    import PIL.Image
    from pyglet.gl import *
    from pyglet.window import key, mouse


class NoWindow:
    """
    Class simulating an window for the no-window mode
    todo: add some more functions here
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

    def set_fullscreen(self, state: bool):
        pass

    def set_size(self, width, height):
        pass

    def set_minimum_size(self, width, height):
        pass

    def set_maximum_size(self, width, height):
        pass


@onlyInClient()
class Window(
    pyglet.window.Window if not shared.NO_WINDOW and shared.IS_CLIENT else NoWindow
):
    """
    Class representing the game window.
    Interacts with the pyglet backend.

    todo: move the pyglet-engine-calls to here to make it possible to exchange the backend
    """

    def __init__(self, *args, **kwargs):
        """
        Creates a new window-instance
        :param args: args send to pyglet.window.Window-constructor
        :param kwargs: kwargs send to pyglet.window.Window-constructor
        """

        super(Window, self).__init__(*args, **kwargs)

        # write window instance to globals.py for sharing
        shared.window = self

        # Whether the window exclusively captures the mouse.
        self.exclusive = False

        # Which sector the player is currently in.
        self.sector = None  # todo: move to player

        # Velocity in the y (upward) direction.
        self.dy = 0  # todo: move to player

        if shared.IS_CLIENT:
            # Convenience list of num keys, todo: move to config.py
            self.num_keys = [
                key._1,
                key._2,
                key._3,
                key._4,
                key._5,
                key._6,
                key._7,
                key._8,
                key._9,
            ]
            self.keys = key.KeyStateHandler()  # key handler from pyglet

            # storing mouse information todo: use pyglet's mouse handler
            self.mouse_pressing = {
                mouse.LEFT: False,
                mouse.RIGHT: False,
                mouse.MIDDLE: False,
            }
            self.mouse_position = (0, 0)

        if shared.IS_CLIENT:
            # The label that is displayed in the top left of the canvas.  todo: move to separated class
            self.label = pyglet.text.Label(
                "",
                font_name="Arial",
                font_size=10,
                x=10,
                y=self.height - 10,
                anchor_x="left",
                anchor_y="top",
                color=(0, 0, 0, 255),
            )
            self.label2 = pyglet.text.Label(
                "",
                font_name="Arial",
                font_size=10,
                x=10,
                y=self.height - 22,
                anchor_x="left",
                anchor_y="top",
                color=(0, 0, 0, 255),
            )
            self.label3 = pyglet.text.Label(
                "",
                font_name="Arial",
                font_size=10,
                x=self.width - 10,
                y=self.height - 34,
                anchor_x="right",
                anchor_y="top",
                color=(0, 0, 0, 255),
            )

        # todo: move both to separated class
        self.cpu_usage = psutil.cpu_percent(interval=None)
        self.cpu_usage_timer = 0

        # todo: move to separated class
        self.CROSSHAIRS_TEXTURE = None

    def load(self):
        # This call schedules the `update()` method to be called 20 times per sec. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 0.05)

        mcpython.common.state.StateHandler.load_states()

        self.push_handlers(self.keys)

        if shared.IS_CLIENT:
            self.CROSSHAIRS_TEXTURE = mcpython.util.texture.to_pyglet_image(
                asyncio.get_event_loop()
                .run_until_complete(
                    mcpython.engine.ResourceLoader.read_image("gui/icons")
                )
                .crop((0, 0, 15, 15))
                .resize((30, 30), PIL.Image.NEAREST)
            )

        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:game_crash", self.close
        )
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:copy_block_or_entity_data", self.get_block_entity_info
        )

    def reset_caption(self):
        """
        Will set the caption of the window to the default one
        """
        self.set_caption(
            "mcpython 4 - {}".format(mcpython.common.config.FULL_VERSION_NAME)
        )

    def set_exclusive_mouse(self, exclusive: bool):
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
        todo: move to player or some util system
        """
        x, y, _ = shared.world.get_active_player().rotation
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

    def update(self, dt: float):
        """
        This method is scheduled to be called repeatedly by the pyglet clock.
        :param dt: The change in time since the last call.
        """

        shared.event_handler.call("gameloop:tick:start", dt)

        self.cpu_usage_timer += dt
        if self.cpu_usage_timer > mcpython.common.config.CPU_USAGE_REFRESH_TIME:
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.cpu_usage_timer = 0

        # todo: change to attribute in State-class
        if dt > 3 and shared.state_handler.active_state.NAME not in [
            "minecraft:mod_loading"
        ]:
            logger.println(
                "[warning] running behind normal tick, did you overload game? missing "
                + str(dt - 0.05)
                + " seconds"
            )

        # todo: move this to the respective state parts
        if any(
            type(x) == mcpython.common.state.GameViewStatePart.GameView
            for x in shared.state_handler.active_state.parts
        ):
            asyncio.get_event_loop().run_until_complete(
                shared.world_generation_handler.task_handler.process_tasks(timer=0.02)
            )

        shared.event_handler.call("tickhandler:general", dt)

    @onlyInClient()
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
        shared.event_handler.call("user:mouse:press", x, y, button, modifiers)

    @onlyInClient()
    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when an button is released with the same argument as on_mouse_press
        """
        self.mouse_pressing[button] = False
        shared.event_handler.call("user:mouse:release", x, y, button, modifiers)

    @onlyInClient()
    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        """
        Called when the mouse moves over the screen while one or more buttons are pressed
        :param x: the new x position
        :param y: the new y position
        :param dx: the delta x
        :param dy: the delta y
        :param buttons: the buttons pressed
        :param modifiers: the modifiers pressed
        """
        self.mouse_position = (x, y)
        shared.event_handler.call("user:mouse:drag", x, y, dx, dy, buttons, modifiers)
        if self.exclusive:
            self.on_mouse_motion(x, y, dx, dy)

    @onlyInClient()
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """
        Called by pyglet when the mouse wheel is spun
        :param x: the new x scroll
        :param y: the new y scroll
        :param scroll_x: the delta x
        :param scroll_y: the delta y
        """
        shared.event_handler.call("user:mouse:scroll", x, y, scroll_x, scroll_y)

    @onlyInClient()
    def on_mouse_motion(self, x: int, y: int, dx: float, dy: float):
        """
        Called when the player moves the mouse.

        :param x y: The coordinates of the mouse click. Always center of the screen if the mouse is captured.
        :param dx dy: The movement of the mouse.

        todo: use pyglet's MouseHandler for tracking the mouse position and buttons
        """
        shared.event_handler.call("user:mouse:motion", x, y, dx, dy)
        self.mouse_position = (x, y)

    @onlyInClient()
    def on_key_press(self, symbol: int, modifiers: int):
        """
        Called when the player presses a key. See pyglet docs for key mappings.
        :param symbol: Number representing the key that was pressed.
        :param modifiers: Number representing any modifying keys that were pressed.
        """
        shared.event_handler.call("user:keyboard:press", symbol, modifiers)

        if symbol == key.P and modifiers & key.MOD_ALT:
            if shared.profiler is None:
                print("enabling profiler")
                shared.profiler = cProfile.Profile()
                shared.profiler.enable()

            else:
                print("stopping profiler & printing results")
                shared.profiler.disable()
                shared.profiler.print_stats("cumtime")
                # os.makedirs(shared.build+"/profiles", exist_ok=True)
                # shared.profiler.dump_stats(shared.build+"/profiles/"+str(time.time())+".txt")
                shared.profiler = None

    @onlyInClient()
    def on_key_release(self, symbol, modifiers):
        """
        Called when the player releases a key. See pyglet docs for key mappings.
        :param symbol: Number representing the key that was pressed.
        :param modifiers: Number representing any modifying keys that were pressed.
        """
        shared.event_handler.call("user:keyboard:release", symbol, modifiers)

    @onlyInClient()
    def on_resize(self, width: int, height: int):
        """
        Called when the window is resized to a new `width` and `height`.
        """
        # labels todo: move to separated class
        self.label.y = height - 10
        self.label2.y = height - 22
        self.label3.x = width - 10
        self.label3.y = height - 34
        shared.event_handler.call("user:window:resize", width, height)

    if shared.IS_CLIENT:

        @name_is_static("pyglet", lambda: pyglet)
        @onlyInClient()
        def set_2d(self):
            # todo: move to RenderingHelper
            width, height = self.get_size()
            viewport = self.get_viewport_size()
            mcpython.engine.rendering.util.set_2d(
                (max(1, viewport[0]), max(1, viewport[1])),
                max(1, width),
                max(1, height),
            )
            pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)

        @name_is_static("pyglet", lambda: pyglet)
        @onlyInClient()
        def set_3d(self, position=None, rotation=None):
            # todo: move to RenderingHelper
            if shared.world.get_active_player() is None:
                return

            if shared.rendering_helper.default_3d_stack is None:
                shared.rendering_helper.default_3d_stack = (
                    shared.rendering_helper.get_dynamic_3d_matrix_stack()
                )

            shared.rendering_helper.default_3d_stack.apply()
            pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)

        @name_is_static("pyglet", lambda: pyglet)
        @onlyInClient()
        def on_draw(self):
            """
            Called by pyglet to draw the canvas.
            todo: move to separated configurable rendering pipeline
            """
            shared.rendering_helper.deleteSavedStates()  # make sure that everything is cleared
            # make sure that the state of the rendering helper is saved for later usage
            state = shared.rendering_helper.save_status(False)

            self.clear()  # clear the screen
            pyglet.gl.glClearColor(1, 1, 1, 1)

            mcpython.engine.rendering.RenderingLayerManager.manager.draw()

            shared.rendering_helper.apply(state)
            shared.rendering_helper.deleteSavedStates()

    @onlyInClient()
    def draw_focused_block(self):
        """
        Draw black edges around the block that is currently under the crosshairs.
        todo: move to special helper class
        """
        vector = self.get_sight_vector()
        block = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )[0]
        if block:
            block = shared.world.get_active_dimension().get_block(block)
            if block:
                block.get_view_bbox().draw_outline(block.position)
                return block

    @onlyInClient()
    def draw_label(self):
        """
        Draw the label in the top left of the screen.
        todo: move to special helper class
        """
        x, y, z = shared.world.get_active_player().position
        nx, ny, nz = mcpython.util.math.normalize(
            shared.world.get_active_player().position
        )
        if not shared.world.gamerule_handler.table["showCoordinates"].status.status:
            x = y = z = "?"
        chunk = shared.world.get_active_dimension().get_chunk(
            *mcpython.util.math.position_to_chunk(
                shared.world.get_active_player().position
            ),
            create=False,
        )
        self.label.text = (
            "%02d (%.2f, %.2f, %.2f) [region %01d %01d], gamemode %01d"
            % (
                pyglet.clock.get_fps(),
                x,
                y,
                z,
                x // 16 // 32,
                z // 16 // 32,
                shared.world.get_active_player().gamemode,
            )
        )

        vector = shared.window.get_sight_vector()
        blockpos, previous, hitpos = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )

        if blockpos:
            blockname = shared.world.get_active_dimension().get_block(blockpos)
            if type(blockname) != str:
                blockname = blockname.NAME

            self.label2.text = "looking at '{}(position={})'".format(
                blockname,
                blockpos
                if shared.world.gamerule_handler.table["showCoordinates"].status.status
                else ("?", "?", "?"),
            )
            self.label2.draw()
            self.label3.y = self.height - 34
        else:
            self.label3.y = self.height - 22

        if chunk:
            biomemap = chunk.get_map("minecraft:biome_map")
            biome = biomemap.get_at_xyz(nx, 0, nz)
            if biome is not None:
                self.label.text += ", biome: " + str(biome)
        self.label.draw()

        process = psutil.Process()
        mem_info = process.memory_info()
        used_m = mem_info.rss
        total_m = psutil.virtual_memory().total
        with process.oneshot():
            self.label3.text = "CPU usage: {}%; Memory usage: {}MB/{}MB ({}%)".format(
                self.cpu_usage,
                used_m // 2**20,
                total_m // 2**20,
                round(used_m / total_m * 10000) / 100,
            )
        self.label3.draw()

    def get_block_entity_info(self):
        """
        used by hotkey for copying entity data to the clipboard
        todo: move to special helper class
        """
        import clipboard

        vector = self.get_sight_vector()
        blockpos, previous, hitpos = shared.world.hit_test(
            shared.world.get_active_player().position, vector
        )
        if blockpos:
            blockname = shared.world.get_active_dimension().get_block(blockpos)
            if type(blockname) != str:
                blockname = blockname.NAME
            clipboard.copy(blockname)

    @onlyInClient()
    def draw_reticle(self):
        """
        Draw the crosshairs in the center of the screen.
        todo: move to special helper class
        """
        pyglet.gl.glColor3d(255, 255, 255)
        wx, wy = self.get_size()
        self.CROSSHAIRS_TEXTURE.blit(
            wx // 2 - self.CROSSHAIRS_TEXTURE.width // 2,
            wy // 2 - self.CROSSHAIRS_TEXTURE.height // 2,
        )

    def on_text(self, text: str):
        """
        Called by pyglet with decoded key values when an text is entered
        :param text: the text entered
        """
        shared.event_handler.call("user:keyboard:enter", text)

    def on_close(self):
        """
        Called when the window tries to close itself
        cleans up some stuff before closing
        """
        if shared.world.save_file.save_in_progress:
            return

        if shared.world.world_loaded:
            # have we a world which should be saved?
            asyncio.get_event_loop().run_until_complete(
                shared.world.get_active_player().inventory_main.remove_items_from_crafting()
            )

            if shared.IS_NETWORKING:
                asyncio.get_event_loop().run_until_complete(
                    shared.NETWORK_MANAGER.disconnect()
                )
            else:
                # make sure that file size is as small as possible
                try:
                    asyncio.get_event_loop().run_until_complete(
                        shared.world.save_file.save_world_async(override=True)
                    )
                except KeyboardInterrupt:
                    logger.println(
                        "[FATAL] interrupted during saving the world; world is likely corrupted!"
                    )

        self.set_fullscreen(False)
        self.close()
