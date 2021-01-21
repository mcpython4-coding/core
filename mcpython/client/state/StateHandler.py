"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
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

    def _switch_to(self, statename: str):
        if statename not in self.states:
            logger.print_stack("state '{}' does not exists".format(statename))
            sys.exit(-10)
        self.CANCEL_SWITCH_STATE = False
        shared.event_handler.call("state:switch:pre", statename)
        if self.CANCEL_SWITCH_STATE:
            return
        if self.active_state:
            self.active_state.deactivate()
        self.active_state: State.State = self.states[statename]
        self.active_state.activate()
        self.active_state.eventbus.call("user:window:resize", *shared.window.get_size())
        shared.event_handler.call("state:switch:post", statename)
        logger.println(
            "[STATE HANDLER][STATE CHANGE] state changed to '{}'".format(statename),
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
