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
import asyncio
import typing

import mcpython.common.event.TickHandler
import mcpython.common.state.ConfigStateFactory
from mcpython import shared
from mcpython.engine import logger

from . import AbstractState


class StateHandler:
    """
    Manager for states of the game.

    The game is a state machine, so we need somebody to keep track of it...
    Seems to be this class

    How does it work?
    - One instance per game, more will break stuff
    - stored @ shared.state_handler
    """

    def __init__(self):
        self.active_state: typing.Optional[AbstractState.AbstractState] = None
        self.states: typing.Dict[str, AbstractState] = {}
        self.global_key_bind_toggle = False

    async def change_state(self, state_name: str, immediate=True):
        """
        Will change the current state of the "machine"
        :param state_name: the name to switch to
        :param immediate: now or next scheduled event cycle (so afterwards), defaults to True
        """
        if state_name not in self.states:
            logger.print_stack("state '{}' does not exists".format(state_name))
            return

        if not shared.IS_CLIENT:
            logger.println(f"[STATE] {state_name}")

        if immediate:
            await self.inner_change_state(state_name)
        else:
            mcpython.common.event.TickHandler.handler.schedule_once(
                self.inner_change_state(state_name)
            )

    async def inner_change_state(self, state_name: str):
        """
        Internal change_state

        DO NOT USE!
        """

        previous = self.active_state.NAME if self.active_state is not None else None

        await shared.event_handler.call_async("state:switch:pre", state_name)

        if self.active_state:
            await self.active_state.deactivate()

        self.active_state: AbstractState.AbstractState = self.states[state_name]
        await self.active_state.activate()

        if shared.IS_CLIENT:
            await self.active_state.eventbus.call_async(
                "user:window:resize", *shared.window.get_size()
            )

        await shared.event_handler.call_async("state:switch:post", state_name)
        logger.println(
            f"[STATE HANDLER][STATE CHANGE] state changed to '{state_name}' (from {repr(previous)})'",
            console=False,
        )

    def add_state(self, state_instance: AbstractState.AbstractState):
        self.states[state_instance.NAME] = state_instance

        if state_instance.CONFIG_LOCATION is not None:
            mcpython.common.state.ConfigStateFactory.get_config(
                state_instance.CONFIG_LOCATION
            ).inject(state_instance)

    def update_mouse_exclusive_state(self):
        shared.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = shared.state_handler = StateHandler()


def load_states():
    import mcpython.client.gui.ContainerRenderingManager

    from . import (
        BlockItemGeneratorState,
        EscapeMenuState,
        GameState,
        ModLoadingProgressState,
        ServerConnectionState,
        ServerSelectionState,
        StartMenuState,
        WorldGenerationConfigState,
        WorldListState,
    )

    # this is the first state, so initial init for it
    asyncio.run(
        handler.change_state("minecraft:mod_loading")
    )
