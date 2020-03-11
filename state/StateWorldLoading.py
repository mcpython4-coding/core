"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State
import state.ui.UIPartLable
import globals as G
import util.math
from pyglet.window import key
import pyglet
import random
import mod.ModMcpython
import state.StatePartConfigBackground
import logger
import chat.DataPack
import time
import util.opengl
import traceback


class StateWorldGeneration(State.State):
    NAME = "minecraft:world_loading"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}
        self.world_size = ((0, 0), (0, 0, 0, 0), 0)
        self.finished_chunks = 0

    def get_parts(self) -> list:
        return [state.StatePartConfigBackground.StatePartConfigBackground(),
                state.ui.UIPartLable.UIPartLable("0%", (0, 50), anchor_lable="MM", anchor_window="MD",
                                                 color=(255, 255, 255, 255))]

    def on_update(self, dt):
        G.world.process_tasks(timer=0.8)
        for chunk in self.status_table:
            self.status_table[chunk] = int(len(G.world.get_active_dimension().get_chunk(*chunk).blockmap) == 0)
        if all(self.status_table.values()):
            G.statehandler.switch_to("minecraft:game")

    def on_activate(self):
        self.status_table.clear()
        G.dimensionhandler.init_dims()
        try:
            G.world.savefile.load_world()
        except IOError:
            logger.println("failed to load world. data-fixer failed with NoDataFixerFoundException")
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:startmenu")
            return
        except:
            logger.println("failed to load world")
            logger.write_exception()
            traceback.print_exc()
            G.statehandler.switch_to("minecraft:startmenu")
            return
        for cx in range(-3, 4):
            for cz in range(-3, 4):
                self.status_table[(cx, cz)] = 0
                G.world.savefile.read("minecraft:chunk", dimension=G.world.active_dimension, chunk=(cx, cz),
                                      immediate=False)

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d", self.on_draw_2d_post)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:startmenu")
            G.tickhandler.schedule_once(G.world.cleanup)
            logger.println("interrupted world loading by user")

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        if len(self.status_table) == 0:
            self.parts[1].text = "0%"
        else:
            self.parts[1].text = "{}%".format(
                round(list(self.status_table.values()).count(1)/len(self.status_table)*1000)/10)

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            else:
                color = (136, 0, 255)
            util.opengl.draw_rectangle((mx+cx*10, my+cz*10), (10, 10), color)


worldloading = None


def create():
    global worldloading
    worldloading = StateWorldGeneration()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

