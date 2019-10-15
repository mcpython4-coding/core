"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import event.EventBus
import traceback


class EventHandler:
    def __init__(self):
        self.buses = []
        self.active_buses = []

    def create_bus(self, *args, active=True, **kwargs) -> event.EventBus.EventBus:
        bus = event.EventBus.EventBus(*args, **kwargs)
        self.buses.append(bus)
        if active: self.active_buses.append(bus)
        return bus

    def activate_bus(self, bus: event.EventBus.EventBus):
        if bus in self.active_buses: return
        self.active_buses.append(bus)

    def deactivate_bus(self, bus: event.EventBus.EventBus):
        if bus not in self.active_buses: return
        self.active_buses.remove(bus)

    def call(self, eventname, *args, **kwargs):
        results = []
        for bus in self.active_buses:
            results += bus.call(eventname, *args, *kwargs)

    def __call__(self, *args, **kwargs): self.call(*args, **kwargs)


G.eventhandler = EventHandler()

PUBLIC_EVENT_BUS = G.eventhandler.create_bus(crash_on_error=False)

