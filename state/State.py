"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry


class State(event.Registry.IRegistryContent):
    @staticmethod
    def is_mouse_exclusive():
        return False

    def __init__(self):
        self.parts = self.get_parts()
        G.statehandler.add_state(self)
        self.eventbus = G.eventhandler.create_bus(active=False, crash_on_error=False)
        self.bind_to_eventbus()
        for statepart in self.parts:
            statepart.master = [self]  # StateParts get an list of steps to get to them as an list
            statepart.bind_to_eventbus()  # Ok, you can now assign to these event bus

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

    def bind_to_eventbus(self):
        pass

    def get_parts(self) -> list:
        return []

    def on_activate(self):  # todo: remove
        pass

    def on_deactivate(self):  # todo: remove
        pass

