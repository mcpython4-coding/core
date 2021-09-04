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
import sys
import time
import typing

import mcpython.client.state.ConfigStateFactory
import mcpython.common.event.TickHandler
from mcpython import shared
from mcpython.engine import logger
from mcpython.util.annotation import onlyInClient

from . import AbstractState


@onlyInClient()
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

    def change_state(self, state_name: str, immediate=True):
        """
        Will change the current state of the "machine"
        :param state_name: the name to switch to
        :param immediate: now or next scheduled event cycle (so afterwards), defaults to True
        """
        if state_name not in self.states:
            logger.print_stack("state '{}' does not exists".format(state_name))
            return

        if immediate:
            self.inner_change_state(state_name)
        else:
            mcpython.common.event.TickHandler.handler.schedule_once(
                self.inner_change_state, state_name
            )

    def inner_change_state(self, state_name: str):
        """
        Internal change_state

        DO NOT USE!
        """

        previous = self.active_state.NAME if self.active_state is not None else None

        shared.event_handler.call("state:switch:pre", state_name)

        if self.active_state:
            self.active_state.deactivate()

        self.active_state: AbstractState.AbstractState = self.states[state_name]
        self.active_state.activate()
        self.active_state.eventbus.call("user:window:resize", *shared.window.get_size())
        shared.event_handler.call("state:switch:post", state_name)
        logger.println(
            f"[STATE HANDLER][STATE CHANGE] state changed to '{state_name}' (from {repr(previous)})'",
            console=False,
        )

    def add_state(self, state_instance: AbstractState.AbstractState):
        self.states[state_instance.NAME] = state_instance

        if state_instance.CONFIG_LOCATION is not None:
            mcpython.client.state.ConfigStateFactory.get_config(
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
        GameInfoState,
        GameState,
        ModLoadingProgressState,
        StartMenuState,
        WorldGenerationConfigState,
        ServerSelectionState,
        ServerConnectionState,
        WorldListState,
    )

    # this is the first state, so initial init for it
    handler.change_state("minecraft:mod_loading")
