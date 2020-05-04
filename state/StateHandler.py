"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import State
import logger
import event.TickHandler


class StateHandler:
    def __init__(self):
        self.active_state: State.State or None = None
        self.states = {}
        self.CANCEL_SWITCH_STATE = False

    def switch_to(self, statename: str or None, immediate=True):
        if immediate:
            self._switch_to(statename)
        else:
            event.TickHandler.handler.schedule_once(self._switch_to, statename)

    def _switch_to(self, statename):
        if statename not in self.states:
            logger.println("[WARNING] state {} does not exists".format(statename))
            return
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

    def add_state(self, state: State.State):
        self.states[state.NAME] = state

    def update_exclusive(self):
        G.window.set_exclusive_mouse(self.active_state.is_mouse_exclusive())


handler = G.statehandler = StateHandler()


def load():
    from . import (StateGame, StateEscape, StateStartMenu, StateGameInfo, StateBlockItemGenerator,
                   StateWorldGenerationConfig, StateModLoading)
    import gui.InventoryHandler

    handler.switch_to("minecraft:modloading")

