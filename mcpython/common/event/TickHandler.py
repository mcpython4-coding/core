"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import pyglet
import mcpython.util.math
import random
import mcpython.common.config
import mcpython.common.DataPack
import mcpython.client.state.StatePartGame


class TickHandler:
    """
    main handler for ticks
    """

    def __init__(self):
        self.tick_array = {}
        self.active_tick = 0
        self.next_ticket_id = 0
        self.results = {}
        pyglet.clock.schedule_interval(self.tick, 1 / 20)
        self.lost_time = 0
        self.enable_tick_skipping = False
        self.instant_ticks = False
        self.enable_random_ticks = True
        # an array of (function, args, kwargs) for functions which should be executed in near future
        self.execute_array = []

    def tick(self, dt):
        """
        execute ticks
        :param dt: the time that came after the last event
        """
        self.active_tick += 1
        self.lost_time += dt
        # execute functions
        while self.lost_time > 1 / 20:
            self.lost_time -= 1 / 20
            if self.active_tick in self.tick_array:
                for ticketid, function, args, kwargs, ticketupdate in self.tick_array[
                    self.active_tick
                ]:
                    result = function(*args, **kwargs)
                    if ticketid:
                        self.results[ticketid] = result
                        ticketupdate(self, ticketid, function, args, kwargs)
                if not self.enable_tick_skipping:
                    self.lost_time = 0
                    return
        G.entity_handler.tick(dt)
        if any(
            type(x) == mcpython.client.state.StatePartGame.StatePartGame
            for x in G.state_handler.active_state.parts
        ):
            mcpython.common.DataPack.datapack_handler.try_call_function(
                "#minecraft:tick"
            )
            if self.enable_random_ticks:
                pyglet.clock.schedule_once(self.send_random_ticks, 0)
        while len(self.execute_array) > 0:
            func, args, kwargs = tuple(self.execute_array.pop(0))
            try:
                func(*args, **kwargs)
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
        cx, cz = mcpython.util.math.positionToChunk(
            G.world.get_active_player().position
        )
        for dx in range(
            -mcpython.common.config.RANDOM_TICK_RANGE,
            mcpython.common.config.RANDOM_TICK_RANGE + 1,
        ):
            for dz in range(
                -mcpython.common.config.RANDOM_TICK_RANGE,
                mcpython.common.config.RANDOM_TICK_RANGE + 1,
            ):
                if dx ** 2 + dz ** 2 <= mcpython.common.config.RANDOM_TICK_RANGE ** 2:
                    x = cx + dx
                    z = cz + dz
                    for dy in range(16):
                        for _ in range(
                            G.world.gamerule_handler.table[
                                "randomTickSpeed"
                            ].status.status
                        ):
                            ddx, ddy, ddz = (
                                random.randint(0, 15),
                                random.randint(0, 255),
                                random.randint(0, 15),
                            )
                            position = (x + ddx, ddy, z + ddz)
                            blockinst = G.world.get_active_dimension().get_block(
                                position
                            )
                            if blockinst is not None and type(blockinst) != str:
                                if blockinst.ENABLE_RANDOM_TICKS:
                                    blockinst.on_random_update()


handler = G.tick_handler = TickHandler()
