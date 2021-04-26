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
import time

from mcpython import shared, logger
from . import State
import mcpython.common.event.TickHandler
import mcpython.client.state.StateConfigFile
import sys
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateHandler:
    def __init__(self):
        self.active_state: State.State or None = None
        self.states = {}
        self.CANCEL_SWITCH_STATE = False

    def switch_to(self, state_name: str, immediate=True):
        assert state_name is not None
        if immediate:
            self._switch_to(state_name)
        else:
            mcpython.common.event.TickHandler.handler.schedule_once(
                self._switch_to, state_name
            )

    def _switch_to(self, state_name: str):
        if state_name not in self.states:
            logger.print_stack("state '{}' does not exists".format(state_name))
            sys.exit(-10)

        previous = self.active_state.NAME if self.active_state is not None else None
        now = time.time()

        shared.event_handler.call("state:switch:pre", state_name)

        if self.active_state:
            self.active_state.deactivate()

        self.active_state: State.State = self.states[state_name]
        self.active_state.activate()
        self.active_state.eventbus.call("user:window:resize", *shared.window.get_size())
        shared.event_handler.call("state:switch:post", state_name)
        logger.println(
            f"[STATE HANDLER][STATE CHANGE] state changed to '{state_name}' (from {repr(previous)}) took {time.time()-now}s'",
            console=False,
        )

    def add_state(self, state_instance: State.State):
        self.states[state_instance.NAME] = state_instance
        if state_instance.CONFIG_LOCATION is not None:
            mcpython.client.state.StateConfigFile.get_config(
                state_instance.CONFIG_LOCATION
            ).inject(state_instance)

    def update_exclusive(self):
        shared.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = shared.state_handler = StateHandler()


@onlyInClient()
def load():
    from . import (
        StateGame,
        StateEscape,
        StateStartMenu,
        StateGameInfo,
        StateBlockItemGenerator,
        StateWorldGenerationConfig,
        StateModLoading,
    )
    import mcpython.client.gui.InventoryHandler

    # todo: add client-check

    handler.switch_to(
        "minecraft:modloading"
    )  # this is the first state todo: make config for it
