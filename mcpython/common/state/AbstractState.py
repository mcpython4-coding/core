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
import typing
from abc import ABC

from mcpython import shared
from mcpython.common.event.api import IRegistryContent
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class AbstractState(IRegistryContent, ABC):
    """
    Base class for all states
    Handled by the StateHandler of the game

    activate() is invoked when the state is switched to, deactivate() when switching away
    bind_to_eventbus() is a helper function for registering functions to the internal event bus
    (It should be used as it is automatically bind when the state is active)

    get_parts() is the initializer for the "parts" attribute and can be used to return a list of StatePart's,
    bound also when needed
    """

    # Set this if the state is mouse-exclusive, so the mouse is hidden
    # For more finer control, use the is_mouse_exclusive() getter method
    IS_MOUSE_EXCLUSIVE = False

    # Default location: data/{mod}/states/{name}.json
    CONFIG_LOCATION: typing.Optional[str] = None

    @classmethod
    def is_mouse_exclusive(cls) -> bool:  # todo: make attribute
        return cls.IS_MOUSE_EXCLUSIVE

    def __init__(self):
        # Internal attribute used when loading serialized states, as they have named their StateParts internally
        self.part_dict = {}

        # Constructs the underlying parts array
        self.eventbus = shared.event_handler.create_bus(
            active=False, crash_on_error=False
        )

        self.parts = self.get_parts()

        for state_part in self.parts:
            # StateParts get an list of steps to get to them as an list
            state_part.master = [self]

        self.bind_to_eventbus()

        for state_part in self.parts:
            # Ok, you can now assign to these event bus
            state_part.bind_to_eventbus()

        if shared.IS_CLIENT:
            import pyglet

            self.underlying_batch = pyglet.graphics.Batch()

            self.state_renderer = self.create_state_renderer()

            if self.state_renderer is not None:
                self.eventbus.subscribe("render:draw:2d", self.state_renderer.draw)
                self.state_renderer.assigned_state = self
                self.state_renderer.batch = self.underlying_batch

                self.state_renderer.init()

            for state in self.parts:
                state.init_rendering()

        else:
            self.state_renderer = None
            self.underlying_batch = None

        shared.state_handler.add_state(self)

    def create_state_renderer(self) -> typing.Any:
        pass

    def activate(self):
        self.eventbus.activate()

        for part in self.parts:
            part.activate()

        if self.state_renderer is not None:
            self.state_renderer.on_activate()

    def deactivate(self):
        self.eventbus.deactivate()

        for part in self.parts:
            part.deactivate()

        if self.state_renderer is not None:
            self.state_renderer.on_deativate()

    def bind_to_eventbus(self):
        pass

    def get_parts(self) -> list:
        return []
