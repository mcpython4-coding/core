"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
from mcpython.common.event.Registry import IRegistryContent
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class State(IRegistryContent):
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
        self.eventbus = G.event_handler.create_bus(active=False, crash_on_error=False)
        self.bind_to_eventbus()
        for statepart in self.parts:
            statepart.master = [
                self
            ]  # StateParts get an list of steps to get to them as an list
            statepart.bind_to_eventbus()  # Ok, you can now assign to these event bus
        G.state_handler.add_state(self)

    def activate(self):
        self.eventbus.activate()
        for part in self.parts:
            part.activate()

    def deactivate(self):
        self.eventbus.deactivate()
        for part in self.parts:
            part.deactivate()

    def bind_to_eventbus(self):
        pass

    def get_parts(self) -> list:
        return []
