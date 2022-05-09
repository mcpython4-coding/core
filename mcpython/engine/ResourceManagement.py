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
import io
import json
import typing
import weakref

from mcpython.engine import ResourceLoader as _ResourceLoader


"""class UnconditionalReloadListener:
    # Weak set of all instances, so we can reload
    __INSTANCES = weakref.WeakSet()

    @classmethod
    async def mark_all_dirty(cls):
        # Run all the reload actions in parallel
        await asyncio.gather(
            *(e() for e in cls.__INSTANCES)
        )

    def __init__(self, callback: typing.Callable[[], typing.Awaitable]):
        self.__callback = callback
        self.__enabled = True

        self.__INSTANCES.add(self)

    def enable(self):
        self.__enabled = True

    def disable(self):
        self.__enabled = False

    def is_enabled(self):
        return self.__enabled

    async def reload(self):
        if self.__enabled:
            await self.__callback()
"""


class LazyResource:
    """
    Handler for lazy-referencing data in the resource system
    Comes with stuff for reloading, caching, etc.

    WARNING: all caches are WEAK, meaning they will be cleaned when you delete all references to that object
    todo: add an option to change this

    Use the methods in ResourceLoader only when dynamically loading data where location changes on most of the
    reloads (e.g. on block textures when the model changes)

    Do use this class when it is mostly the same file name, e.g. config files, block states, ...
    We will inform you when it changed, and if you use 'check_for_changes_on_reload' together with 'cache', you
    will be only informed when the content changed
    """

    # Weak set of all instances, so we can reload
    __INSTANCES = weakref.WeakSet()

    @classmethod
    async def mark_all_dirty(cls):
        # Run all the reload actions in parallel
        await asyncio.gather(
            *filter(lambda e: e is not None, [
                await instance.mark_dirty()
                for instance in cls.__INSTANCES
            ])
        )

    def __init__(
        self,
        name: str,
        cache=False,
        callback_on_change: typing.Callable[[], typing.Awaitable] = None,
        check_for_changes_on_reload=False,
    ):
        if name is None:
            raise ValueError("'name' cannot be None")

        if callback_on_change is not None and not callable(callback_on_change):
            raise AssertionError("'callback_on_change' must be None or callable")

        if check_for_changes_on_reload and not cache:
            raise AssertionError("Can only use 'check_for_changes_on_reload' together with 'cache'")

        self.__name = name
        self.__has_cache = cache
        self.__cache = None
        self.__dirty = True
        self.__callback_on_change = callback_on_change
        self.__check_for_changes_on_reload = check_for_changes_on_reload

        self.__pyglet_image_cache = None
        self.__pillow_image_cache = None
        self.__json_cache = None

        self.__INSTANCES.add(self)

    # This is a special async method; It will first run stuff and then return an await-able None-able thingy for running the internal
    async def mark_dirty(self) -> typing.Awaitable | None:
        self.__dirty = True

        # If we have a cache, we can delete it now
        if self.__has_cache:

            if self.__check_for_changes_on_reload:
                new_data = await _ResourceLoader.read_raw(self.__name)

                if new_data == self.__cache:
                    self.__dirty = False
                    return

                self.__cache = new_data
            else:
                self.__cache = None

            self.__pyglet_image_cache = None
            self.__pillow_image_cache = None
            self.__json_cache = None

        if self.__callback_on_change is not None:
            return self.__callback_on_change()

    async def mark_dirty_direct(self):
        result = await self.mark_dirty()
        if result is not None:
            await result

    def is_dirty(self) -> bool:
        return self.__dirty

    async def read_raw(self, unmark_dirty=True) -> bytes:
        if self.__has_cache and not self.__dirty:
            return self.__cache

        data = await _ResourceLoader.read_raw(self.__name)

        if self.__dirty and unmark_dirty:
            if self.__has_cache:
                self.__cache = data

            self.__dirty = False

        return data

    async def read_pyglet_image(self, unmark_dirty=True):
        if (
            self.__has_cache
            and not self.__dirty
            and self.__pyglet_image_cache is not None
        ):
            return self.__pyglet_image_cache

        import pyglet

        data = await self.read_raw(unmark_dirty)
        stream = io.BytesIO(data)

        image = pyglet.image.load(self.__name, stream)

        if self.__dirty and unmark_dirty:
            if self.__has_cache:
                self.__pyglet_image_cache = weakref.proxy(image)

            self.__dirty = False

        return image

    async def read_pillow_image(self, unmark_dirty=True):
        if (
            self.__has_cache
            and not self.__dirty
            and self.__pillow_image_cache is not None
        ):
            return self.__pyglet_image_cache

        import PIL.Image

        data = await self.read_raw(unmark_dirty)
        stream = io.BytesIO(data)

        image = PIL.Image.open(stream)

        if self.__dirty and unmark_dirty:
            if self.__has_cache:
                self.__pillow_image_cache = weakref.proxy(image)

            self.__dirty = False

        return image

    async def read_json(self, unmark_dirty=True):
        if self.__has_cache and not self.__dirty and self.__json_cache is not None:
            return self.__pyglet_image_cache

        data = await self.read_raw(unmark_dirty)
        stream = io.BytesIO(data)

        decoded_data = json.load(stream)

        if self.__dirty and unmark_dirty:
            if self.__has_cache:
                self.__json_cache = weakref.proxy(decoded_data)

            self.__dirty = False

        return decoded_data
