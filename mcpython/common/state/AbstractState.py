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


class AbstractState(IRegistryContent, ABC):
    """
    Base class for all states
    Handled by the StateHandler of the game

    activate() is invoked when the state is switched to, deactivate() when switching away
    bind_to_eventbus() is a helper function for registering functions to the internal event bus
    (It should be used as it is automatically bind when the state is active)

    create_state_parts() is the initializer for the "parts" attribute and can be used to return a list of StatePart's,
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

        self.parts = self.create_state_parts()

        for state_part in self.parts:
            # StateParts get an list of steps to get to them as an list
            state_part.master = [self]
            state_part.eventbus = self.eventbus

        self.bind_to_eventbus()

        for state_part in self.parts:
            # Ok, you can now assign to these event bus
            state_part.bind_to_eventbus()

        if shared.IS_CLIENT:
            import pyglet

            self.underlying_batch = pyglet.graphics.Batch()

            self.state_renderer = self.create_state_renderer()

            if self.state_renderer is not None:
                self.eventbus.subscribe(
                    self.state_renderer.ASSIGNED_DRAW_STAGE, self.state_renderer.draw
                )
                self.eventbus.subscribe(
                    "user:window:resize", self.state_renderer.resize
                )

                self.state_renderer.assigned_state = self
                self.state_renderer.batch = self.underlying_batch

                self.state_renderer.init()

            for state in self.parts:
                shared.tick_handler.schedule_once(state.init_rendering())

        else:
            self.state_renderer = None
            self.underlying_batch = None

        shared.state_handler.add_state(self)

    def create_state_renderer(self) -> typing.Any:
        """
        Optional creates a AbstractStateRenderer instance for this state
        Only invoked on client side
        May return None when no state renderer is needed (e.g. when all is handled somewhere in the parts)
        """

    def create_state_parts(self) -> typing.List:
        """
        Creates the parts of the state (instances of AbstractStatePart)
        When not overwritten, defaults to no state parts
        Invoked somewhere during state construction; Not further defined by API
        WARNING: this might get invoked DURING the constructor of THIS class,
            so invoking super().__init__() will result into this being invoked. When writing to the same variables
            as below the line in the constructor, this will reset the values!
        """
        return []

    def bind_to_eventbus(self):
        """
        Helper method for binding to the internal EventBus
        Invoked somewhere during state construction; Not further defined by API
        """

    async def activate(self):
        self.eventbus.activate()

        for part in self.parts:
            await part.activate()

            if shared.IS_CLIENT:
                await part.init_rendering()

        if self.state_renderer is not None:
            self.state_renderer.on_activate()

    async def deactivate(self):
        self.eventbus.deactivate()

        for part in self.parts:
            await part.deactivate()

        if self.state_renderer is not None:
            self.state_renderer.on_deactivate()
