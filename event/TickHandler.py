"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import pyglet
import util.math
import random
import config
import chat.DataPack


class TickHandler:
    """
    main handler for ticks
    """

    def __init__(self):
        self.tick_array = {}
        self.active_tick = 0
        self.next_ticket_id = 0
        self.results = {}
        pyglet.clock.schedule_interval(self.tick, 1/20)
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
                for ticketid, function, args, kwargs, ticketupdate in self.tick_array[self.active_tick]:
                    result = function(*args, **kwargs)
                    if ticketid:
                        self.results[ticketid] = result
                        ticketupdate(self, ticketid, function, args, kwargs)
                if not self.enable_tick_skipping:
                    self.lost_time = 0
                    return
        if self.enable_random_ticks:
            pyglet.clock.schedule_once(self.send_random_ticks, 0)
        while len(self.execute_array) > 0:
            func, args, kwargs = tuple(self.execute_array.pop(0))
            try:
                func(*args, **kwargs)
            except:
                print(func, args, kwargs)
                raise
        chat.DataPack.datapackhandler.try_call_function("#minecraft:tick")

    def schedule_once(self, function, *args, **kwargs):
        """
        Will execute the function in near time. Helps when in an event and need to exchange stuff which might be
        affected when calling further down the event stack
        :param function: the function to call
        """
        self.execute_array.append((function, args, kwargs))

    def bind(self, function, tick, isdelta=True, ticketfunction=None, args=[], kwargs={}):
        """
        bind an function to an given tick
        :param function: the function to bind
        :param tick: the tick to add
        :param isdelta: if it is delta or not
        :param ticketfunction: function which is called when the function is called with some informations
        :param args: the args to give
        :param kwargs: the kwargs to give
        """
        if self.instant_ticks:
            function(*args, **kwargs)
            return
        if isdelta:
            tick += self.active_tick
        # logger.println(function, tick, self.active_tick)
        if tick not in self.tick_array: self.tick_array[tick] = []
        if ticketfunction:
            ticketid = self.next_ticket_id
            self.next_ticket_id += 1
        else:
            ticketid = None
        self.tick_array[tick].append((ticketid, function, args, kwargs, ticketfunction))

    def bind_redstone_tick(self, function, tick, *args, **kwargs):
        self.bind(function, tick * 2, *args, **kwargs)

    def send_random_ticks(self, *args, **kwargs):
        cx, cz = util.math.sectorize(G.player.position)
        for dx in range(-config.RANDOM_TICK_RANGE, config.RANDOM_TICK_RANGE + 1):
            for dz in range(-config.RANDOM_TICK_RANGE, config.RANDOM_TICK_RANGE + 1):
                if dx ** 2 + dz ** 2 <= config.RANDOM_TICK_RANGE ** 2:
                    x = cx + dx
                    z = cz + dz
                    for dy in range(16):
                        for _ in range(G.world.gamerulehandler.table["randomTickSpeed"].status.status):
                            ddx, ddy, ddz = random.randint(0, 15), random.randint(0, 255), random.randint(0, 15)
                            position = (x + ddx, ddy, z + ddz)
                            blockinst = G.world.get_active_dimension().get_block(position)
                            if blockinst is not None and type(blockinst) != str:
                                blockinst.on_random_update()


handler = G.tickhandler = TickHandler()
