"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from .. import globals as G, logger
from . import State
import mcpython.event.TickHandler
import mcpython.state.StateConfigFile
import sys


class StateHandler:
    def __init__(self):
        self.active_state: State.State or None = None
        self.states = {}
        self.CANCEL_SWITCH_STATE = False

    def switch_to(self, statename: str, immediate=True):
        if statename is None: return  # todo: remove
        if immediate:
            self._switch_to(statename)
        else:
            mcpython.event.TickHandler.handler.schedule_once(self._switch_to, statename)

    def _switch_to(self, statename: str):
        if statename not in self.states:
            logger.print_stack("state '{}' does not exists".format(statename))
            sys.exit(-10)
        self.CANCEL_SWITCH_STATE = False
        G.eventhandler.call("state:switch:pre", statename)
        if self.CANCEL_SWITCH_STATE: return
        if self.active_state:
            self.active_state.deactivate()
        self.active_state: State.State = self.states[statename]
        self.active_state.activate()
        self.active_state.eventbus.call("user:window:resize", *G.window.get_size())
        G.eventhandler.call("state:switch:post", statename)
        logger.println("[STATEHANDLER][STATE CHANGE] state changed to '{}'".format(statename), write_into_console=False)

    def add_state(self, state_instance: State.State):
        self.states[state_instance.NAME] = state_instance
        if state_instance.CONFIG_LOCATION is not None:
            mcpython.state.StateConfigFile.get_config(state_instance.CONFIG_LOCATION).inject(state_instance)

    def update_exclusive(self):
        G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = G.statehandler = StateHandler()


def load():
    from . import (StateGame, StateEscape, StateStartMenu, StateGameInfo, StateBlockItemGenerator,
                   StateWorldGenerationConfig, StateModLoading)
    import mcpython.gui.InventoryHandler

    handler.switch_to("minecraft:modloading")  # this is the first state todo: make config for it

