"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import pyglet
import util.math
import random
import config


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

    def tick(self, dt):
        """
        execute ticks
        :param dt: the time that came after the last event
        """
        self.active_tick += 1
        # execute functions
        if self.active_tick in self.tick_array:
            for ticketid, function, args, kwargs, ticketupdate in self.tick_array[self.active_tick]:
                result = function(*args, **kwargs)
                if ticketid:
                    self.results[ticketid] = result
                    ticketupdate(self, ticketid, function, args, kwargs)
        # pyglet.clock.schedule(self.send_random_ticks)

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
        if isdelta:
            tick += self.active_tick
        # print(function, tick, self.active_tick)
        if tick not in self.tick_array: self.tick_array[tick] = []
        if ticketfunction:
            ticketid = self.next_ticket_id
            self.next_ticket_id += 1
        else:
            ticketid = None
        self.tick_array[tick].append((ticketid, function, args, kwargs, ticketfunction))

    def bind_redstone_tick(self, function, tick, *args, **kwargs):
        self.bind(function, tick*2, *args, **kwargs)

    def send_random_ticks(self, *args, **kwargs):
        cx, cz = util.math.sectorize(G.window.position)
        for dx in range(-config.RANDOM_TICK_RANGE, config.RANDOM_TICK_RANGE+1):
            for dz in range(-config.RANDOM_TICK_RANGE, config.RANDOM_TICK_RANGE+1):
                if dx ** 2 + dz ** 2 <= config.RANDOM_TICK_RANGE ** 2:
                    x = cx + dx
                    z = cz + dz
                    for dy in range(16):
                        for _ in range(config.RANDOM_TICK_SPEED):
                            ddx, ddy, ddz = random.randint(0, 15), random.randint(0, 255), random.randint(0, 15)
                            position = (x+ddx, ddy, z+ddz)
                            if position in G.world.world:
                                G.world.world[position].on_random_update()


handler = G.tickhandler = TickHandler()

