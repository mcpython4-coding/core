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
__all__ = ["EventHandler", "PUBLIC_EVENT_BUS", "LOADING_EVENT_BUS"]

import asyncio

from mcpython import shared
from mcpython.engine.event.EventBus import EventBus


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
        return asyncio.get_event_loop().run_until_complete(
            self.call_async(event_name, *args, **kwargs)
        )

    async def call_async(self, event_name, *args, **kwargs):
        await asyncio.gather(
            *(bus.call_async(event_name, *args, **kwargs) for bus in self.active_buses)
        )

    def call_cancelable(self, event_name, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(
            self.call_cancelable_async(event_name, *args, **kwargs)
        )

    async def call_cancelable_async(self, event_name, *args, **kwargs):
        for bus in self.active_buses:
            if (await bus.call_cancelable_async(event_name, *args, **kwargs)).canceled:
                return False
        return True

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)


shared.event_handler = EventHandler()

PUBLIC_EVENT_BUS = shared.event_handler.create_bus(crash_on_error=False)
LOADING_EVENT_BUS = shared.event_handler.create_bus()
