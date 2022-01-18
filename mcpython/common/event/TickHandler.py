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
import gc
import random
import sys
import typing

import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.common.state.GameViewStatePart
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.engine import logger
from mcpython.mixin.optimiser_annotations import (
    access_static,
    constant_arg,
    inline_call,
)

if shared.IS_CLIENT:
    from mcpython.client.texture.AnimationManager import animation_manager


class TickHandler:
    """
    Main handler for ticks
    """

    def __init__(self):
        self.tick_array = {}
        self.active_tick = 0
        self.next_ticket_id = 0
        self.results = {}

        self.lost_time = 0
        self.enable_tick_skipping = False
        self.instant_ticks = False
        self.enable_random_ticks = True

        # an array of (function, args, kwargs) for functions which should be executed in near future
        self.execute_array = []

        pyglet.clock.schedule_interval(self.schedule_tick, 1 / 20)

    def schedule_tick(self, dt: float):
        asyncio.get_event_loop().run_until_complete(self.tick(dt))

    @access_static("shared.IS_CLIENT")
    async def tick(self, dt: float):
        """
        Execute ticks

        Internally applies a small mixin for the IS_CLIENT checks (see OptimiserMixins.py)

        :param dt: the time that came after the last event
        """
        self.lost_time += dt

        # execute functions
        while self.lost_time >= 1 / 20:
            self.lost_time -= 1 / 20
            self.active_tick += 1

            if self.active_tick in self.tick_array:
                for ticket_id, function, args, kwargs, ticket_update in self.tick_array[
                    self.active_tick
                ]:
                    if isinstance(function, typing.Awaitable):
                        result = await function
                    else:
                        result = function(*args, **kwargs)

                        if isinstance(result, typing.Awaitable):
                            result = await result

                    if ticket_id:
                        self.results[ticket_id] = result
                        ticket_update(self, ticket_id, function, args, kwargs)

                # And now do a cleanup
                del self.tick_array[self.active_tick]

                if not self.enable_tick_skipping:
                    self.lost_time = 0
                    break

        await shared.entity_manager.tick(dt)

        if shared.IS_CLIENT:
            shared.inventory_handler.tick(dt)

        shared.world.tick()
        await shared.event_handler.call_async("tickhandler:general", dt)

        if shared.IS_CLIENT:
            await shared.event_handler.call_async("tickhandler:client")
            await shared.NETWORK_MANAGER.fetch_as_client()
            animation_manager.tick(dt * 20)
        else:
            await shared.event_handler.call_async("tickhandler:server")
            await shared.NETWORK_MANAGER.fetch_as_server()

        # todo: include command info here!
        await mcpython.common.data.DataPacks.datapack_handler.try_call_function(
            "#minecraft:tick", None
        )
        if self.enable_random_ticks:
            await self.send_random_ticks(0)

        while len(self.execute_array) > 0:
            func, args, kwargs = tuple(self.execute_array.pop(0))
            try:

                if not isinstance(func, typing.Awaitable):
                    result = func(*args, **kwargs)
                    if isinstance(result, typing.Awaitable):
                        await result
                else:
                    await func

            except (SystemExit, KeyboardInterrupt, OSError) as e:
                logger.print_exception("during invoking ticks")
                sys.exit(-1)

            except:
                logger.print_exception(
                    "exception during invoking",
                    "{}({},{})".format(
                        func,
                        ", ".join(args),
                        ", ".join(["{}={}".format(key, kwargs[key]) for key in kwargs]),
                    ),
                )

    def schedule_once(
        self, function: typing.Callable | typing.Coroutine, *args, **kwargs
    ):
        """
        Will execute the function in near time. Helps when in an event and need to exchange stuff which might be
        affected when calling further down the event stack
        :param function: the function to call
        """
        self.execute_array.append((function, args, kwargs))

    @constant_arg("args")
    @constant_arg("kwargs")
    def bind(
        self,
        function: typing.Callable | typing.Coroutine,
        tick: int,
        is_delta=True,
        ticket_function=None,
        args=[],
        kwargs={},
    ):
        """
        bind an function to an given tick
        :param function: the function to bind
        :param tick: the tick to add
        :param is_delta: if it is delta or not
        :param ticket_function: function which is called when the function is called with some information
        :param args: the args to give
        :param kwargs: the kwargs to give
        """
        if self.instant_ticks:
            function(*args, **kwargs)
            return

        if is_delta:
            tick += self.active_tick

        if tick not in self.tick_array:
            self.tick_array[tick] = []

        if ticket_function:
            ticket_id = self.next_ticket_id
            self.next_ticket_id += 1
        else:
            ticket_id = None

        self.tick_array[tick].append(
            (ticket_id, function, args, kwargs, ticket_function)
        )

    # @inline_call("%.bind", lambda: TickHandler.bind)
    def bind_redstone_tick(self, function, tick, *args, **kwargs):
        self.bind(function, tick * 2, *args, **kwargs)

    @access_static("shared.IS_CLIENT")
    async def send_random_ticks(self, *args, **kwargs):
        # todo: when networking, only on server & walk over all players!
        if not shared.IS_CLIENT:
            return

        dimension = shared.world.get_active_dimension()
        if dimension is None:
            return

        random_tick_speed = shared.world.gamerule_handler.table[
            "randomTickSpeed"
        ].status.status
        r = mcpython.common.config.RANDOM_TICK_RANGE

        blocks = []

        for player in shared.world.players.values():
            cx, cz = mcpython.util.math.position_to_chunk(player.position)
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx ** 2 + dz ** 2 <= r ** 2:
                        x = cx + dx
                        z = cz + dz
                        for dy in range(16):
                            for _ in range(random_tick_speed):
                                ddx, ddy, ddz = (
                                    random.randint(0, 15),
                                    random.randint(0, 15),
                                    random.randint(0, 15),
                                )
                                position = (x + ddx, dy * 16 + ddy, z + ddz)
                                instance = dimension.get_block(position)
                                if (
                                    instance is not None
                                    and type(instance) != str
                                    and instance.ENABLE_RANDOM_TICKS
                                ):
                                    blocks.append(instance.on_random_update())

        await asyncio.gather(*(func for func in blocks if func))


handler = shared.tick_handler = TickHandler()
