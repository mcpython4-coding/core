"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.EventBus


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
LOADING_EVENT_BUS = G.eventhandler.create_bus()

