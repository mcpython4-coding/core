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
import queue
import time
import typing

import pyglet.app
from mcpython.engine import logger


def schedule_task(task):
    if not asyncio.iscoroutine(task):
        ASYNC_INVOKE_QUEUE.put(task())
    else:
        ASYNC_INVOKE_QUEUE.put(task)
    return task


ASYNC_INVOKE_QUEUE = queue.SimpleQueue()


class Lifecycle(pyglet.app.EventLoop):
    def run(self, interval=1 / 60):
        """Begin processing events, scheduled functions and window updates.

        This method returns when :py:attr:`has_exit` is set to True.

        Developers are discouraged from overriding this method, as the
        implementation is platform-specific.
        """
        if not interval:
            self.clock.schedule(self._redraw_windows)
        else:
            self.clock.schedule_interval(self._redraw_windows, interval)

        self.has_exit = False

        from pyglet.window import Window
        Window._enable_event_queue = False

        # Dispatch pending events
        for window in pyglet.app.windows:
            window.switch_to()
            window.dispatch_pending_events()

        platform_event_loop = pyglet.app.platform_event_loop
        platform_event_loop.start()
        self.dispatch_event('on_enter')
        self.is_running = True

        while not self.has_exit:
            timeout = self.idle()
            platform_event_loop.step(timeout)

            self.handle_some_async()

        self.is_running = False
        self.dispatch_event('on_exit')
        platform_event_loop.stop()

    def handle_some_async(self):
        start = time.time()

        # todo: make time configurable
        while time.time() - start < 1 / 60 and not ASYNC_INVOKE_QUEUE.empty():
            task: asyncio.Task | typing.Coroutine = ASYNC_INVOKE_QUEUE.get()

            try:
                asyncio.run(task)
            except:  # lgtm [py/catch-base-exception]
                logger.print_exception(f"During invoking task {task}")
                continue

            if isinstance(task, asyncio.Task):
                ex = task.exception()
                if ex is not None:
                    try:
                        raise ex
                    except:  # lgtm [py/catch-base-exception]
                        logger.print_exception(f"During invoking task {task}")
