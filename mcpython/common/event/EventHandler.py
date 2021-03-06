"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from mcpython.common.event.EventBus import EventBus


class EventHandler:
    def __init__(self):
        self.buses = []
        self.active_buses = []

    def create_bus(self, *args, active=True, **kwargs) -> EventBus:
        bus = EventBus(*args, **kwargs)
        self.buses.append(bus)
        if active:
            self.active_buses.append(bus)
        return bus

    def activate_bus(self, bus: EventBus):
        if bus in self.active_buses:
            return
        self.active_buses.append(bus)

    def deactivate_bus(self, bus: EventBus):
        if bus not in self.active_buses:
            return
        self.active_buses.remove(bus)

    def call(self, event_name, *args, **kwargs):
        results = []
        for bus in self.active_buses:
            results += bus.call(event_name, *args, *kwargs)

    def call_cancelable(self, event_name, *args, **kwargs):
        for bus in self.active_buses:
            if bus.call_cancelable(event_name, *args, **kwargs).canceled:
                return False
        return True

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)


shared.event_handler = EventHandler()

PUBLIC_EVENT_BUS = shared.event_handler.create_bus(crash_on_error=False)
LOADING_EVENT_BUS = shared.event_handler.create_bus()
