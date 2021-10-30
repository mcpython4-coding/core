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
import random

import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.common.state.GameViewStatePart
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.engine import logger


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

        pyglet.clock.schedule_interval(self.tick, 1 / 20)

    def tick(self, dt):
        """
        Execute ticks
        :param dt: the time that came after the last event
        """
        self.active_tick += 1
        self.lost_time += dt
        # execute functions
        while self.lost_time > 1 / 20:
            self.lost_time -= 1 / 20
            if self.active_tick in self.tick_array:
                for ticket_id, function, args, kwargs, ticket_update in self.tick_array[
                    self.active_tick
                ]:
                    result = function(*args, **kwargs)
                    if ticket_id:
                        self.results[ticket_id] = result
                        ticket_update(self, ticket_id, function, args, kwargs)

                if not self.enable_tick_skipping:
                    self.lost_time = 0
                    return

        shared.entity_manager.tick(dt)

        if shared.IS_CLIENT:
            shared.inventory_handler.tick(dt)

        shared.world.tick()
        shared.event_handler.call("tickhandler:general", dt)

        if shared.IS_CLIENT:
            shared.event_handler.call("tickhandler:client")
            shared.NETWORK_MANAGER.fetch_as_client()
        else:
            shared.event_handler.call("tickhandler:server")
            shared.NETWORK_MANAGER.fetch_as_server()

        # todo: include command info here!
        mcpython.common.data.DataPacks.datapack_handler.try_call_function(
            "#minecraft:tick", None
        )
        if self.enable_random_ticks:
            pyglet.clock.schedule_once(self.send_random_ticks, 0)

        while len(self.execute_array) > 0:
            func, args, kwargs = tuple(self.execute_array.pop(0))
            try:
                func(*args, **kwargs)

            except (SystemExit, KeyboardInterrupt, OSError):
                raise

            except:
                logger.print_exception(
                    "exception during invoking",
                    "{}({},{})".format(
                        func,
                        ", ".join(args),
                        ", ".join(["{}={}".format(key, kwargs[key]) for key in kwargs]),
                    ),
                )

    def schedule_once(self, function, *args, **kwargs):
        """
        Will execute the function in near time. Helps when in an event and need to exchange stuff which might be
        affected when calling further down the event stack
        :param function: the function to call
        """
        self.execute_array.append((function, args, kwargs))

    def bind(
        self, function, tick, is_delta=True, ticket_function=None, args=[], kwargs={}
    ):
        """
        bind an function to an given tick
        :param function: the function to bind
        :param tick: the tick to add
        :param is_delta: if it is delta or not
        :param ticket_function: function which is called when the function is called with some informations
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

    def bind_redstone_tick(self, function, tick, *args, **kwargs):
        self.bind(function, tick * 2, *args, **kwargs)

    def send_random_ticks(self, *args, **kwargs):
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

        # todo: make iterate over all players
        cx, cz = mcpython.util.math.position_to_chunk(
            shared.world.get_active_player().position
        )
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
                                instance.on_random_update()


handler = shared.tick_handler = TickHandler()
