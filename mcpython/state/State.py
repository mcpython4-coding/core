"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.event.Registry


class State(mcpython.event.Registry.IRegistryContent):
    """
    base class
    """

    IS_MOUSE_EXCLUSIVE = False
    CONFIG_LOCATION = None  # default location: data/{mod}/states/{name}.json

    @classmethod
    def is_mouse_exclusive(cls):  # todo: make attribute
        return cls.IS_MOUSE_EXCLUSIVE

    def __init__(self):
        self.part_dict = {}
        self.parts = self.get_parts()  # todo: remove
        self.eventbus = G.eventhandler.create_bus(active=False, crash_on_error=False)
        self.bind_to_eventbus()
        for statepart in self.parts:
            statepart.master = [self]  # StateParts get an list of steps to get to them as an list
            statepart.bind_to_eventbus()  # Ok, you can now assign to these event bus
        G.statehandler.add_state(self)

    def activate(self):
        self.eventbus.activate()
        self.on_activate()
        for statepart in self.parts:
            statepart.activate()

    def deactivate(self):
        self.eventbus.deactivate()
        self.on_deactivate()
        for statepart in self.parts:
            statepart.deactivate()

    def bind_to_eventbus(self):  # todo: remove
        pass

    def get_parts(self) -> list:  # todo: remove
        return []

    def on_activate(self):  # todo: remove
        pass

    def on_deactivate(self):  # todo: remove
        pass

