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
import queue
import time

import pyglet.app
import asyncio

from mcpython.engine import logger


def schedule_task(task):
    if not asyncio.iscoroutine(task):
        ASYNC_INVOKE_QUEUE.put(task())
    else:
        ASYNC_INVOKE_QUEUE.put(task)
    return task


ASYNC_INVOKE_QUEUE = queue.SimpleQueue()


class Lifecycle(pyglet.app.EventLoop):
    def run(self):
        self.has_exit = False
        self._legacy_setup()

        platform_event_loop = pyglet.app.platform_event_loop
        platform_event_loop.start()
        self.dispatch_event("on_enter")
        self.is_running = True

        while not self.has_exit:
            timeout = self.idle()
            platform_event_loop.step(timeout)

            self.handle_some_async()

        self.is_running = False
        self.dispatch_event("on_exit")
        platform_event_loop.stop()

    def handle_some_async(self):
        start = time.time()

        # todo: make time configurable
        while time.time() - start < 1 / 60 and not ASYNC_INVOKE_QUEUE.empty():
            task: asyncio.Task = ASYNC_INVOKE_QUEUE.get()
            asyncio.get_event_loop().run_until_complete(task)

            ex = task.exception()
            if ex is not None:
                try:
                    raise ex
                except:
                    logger.print_exception(f"During invoking task {task}")
