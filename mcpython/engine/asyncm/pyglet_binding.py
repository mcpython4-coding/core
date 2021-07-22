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

import mcpython.engine.asyncm.Manager


class PygletDataManager:
    """
    Binding manager for a pyglet backend with support for async stuff handling
    """

    def __init__(self, side: mcpython.engine.asyncm.Manager.SpawnedProcessInfo):
        self.side = side
        self.windows = []

        import pyglet

        self.event_loop = pyglet.app.event_loop
        self.platform_event_loop = pyglet.app.platform_event_loop

    async def setup(self):
        self.event_loop.has_exit = False
        self.event_loop._legacy_setup()
        self.platform_event_loop.start()
        self.event_loop.dispatch_event("on_enter")
        self.event_loop.is_running = True

        self.side.call_regular = self.step

    async def spawn_default_window(
        self, *args, invoke_with_window=None, on_draw_callback=None, **kwargs
    ):
        import pyglet

        win = pyglet.window.Window(*args, **kwargs)

        @win.event
        def on_close():
            async def close(side):
                side.sided_task_manager.main_obj.stop()

            self.side.sided_task_manager.invokeOnMainNoWait(close)

        @win.event
        def on_draw():
            pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)
            win.clear()

            if on_draw_callback is not None:
                on_draw_callback(win)

        await self._setup_win(win, invoke_with_window=invoke_with_window)

    async def spawn_custom_window(
        self, win_module: str, win_attr: str, *args, invoke_with_window=None, **kwargs
    ):
        import importlib

        module = importlib.import_module(win_module)
        win_class = getattr(module, win_attr)

        win = win_class(*args, **kwargs)
        await self._setup_win(win, invoke_with_window=invoke_with_window)

    async def _setup_win(self, win, invoke_with_window=None):
        win.async_manager = self

        self.windows.append(win)

        if invoke_with_window is not None:
            await invoke_with_window(self, win)

    async def step(self, _):
        # todo: can we do some stuff async?
        timeout = self.event_loop.idle()
        self.platform_event_loop.step(timeout)

    async def check_exit(self):
        if self.event_loop.has_exit:
            self.event_loop.is_running = False
            self.event_loop.dispatch_event("on_exit")
            self.platform_event_loop.stop()
            asyncio.get_running_loop().stop()


def spawn_in(process_manager: mcpython.engine.asyncm.Manager.AsyncProcessManager):
    process_manager.add_process("pyglet")

    async def spawn(side: mcpython.engine.asyncm.Manager.SpawnedProcessInfo):
        print("spawning pyglet side")
        import pyglet

        # This is needed as the code is not executed in the same context
        from mcpython.engine.asyncm.pyglet_binding import PygletDataManager

        side.pyglet_manager = PygletDataManager(side)
        await side.pyglet_manager.setup()

    process_manager.run_regular_on_process("pyglet", spawn)
