"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State
import mcpython.state.ui.UIPartLable
import globals as G
import mcpython.util.math
from pyglet.window import key
import pyglet
import random
import mcpython.mod.ModMcpython
import mcpython.state.StatePartConfigBackground
import logger
import mcpython.chat.DataPack
import time
import mcpython.util.opengl


class StateWorldLoading(State.State):
    NAME = "minecraft:world_loading"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}
        self.world_size = ((0, 0), (0, 0, 0, 0), 0)
        self.finished_chunks = 0

    def get_parts(self) -> list:
        return [mcpython.state.StatePartConfigBackground.StatePartConfigBackground(),
                mcpython.state.ui.UIPartLable.UIPartLable("0%", (0, 50), anchor_lable="MM", anchor_window="MD",
                                                          color=(255, 255, 255, 255)),
                mcpython.state.ui.UIPartLable.UIPartLable("(0/0/0)", (0, 30), anchor_lable="MM", anchor_window="MD",
                                                          color=(255, 255, 255, 255))]

    def on_update(self, dt):
        G.worldgenerationhandler.task_handler.process_tasks(timer=0.8)
        for chunk in self.status_table:
            c = G.worldgenerationhandler.task_handler.get_task_count_for_chunk(
                G.world.get_active_dimension().get_chunk(*chunk))
            self.status_table[chunk] = 1 / c if c > 0 else -1
        if len(G.worldgenerationhandler.task_handler.chunks) == 0:
            G.statehandler.switch_to("minecraft:game")
        self.parts[1].text = "{}%".format(round(sum(self.status_table.values()) / len(self.status_table) * 1000) / 10)

    def on_activate(self):
        G.worldgenerationhandler.enable_generation = False
        self.status_table.clear()
        G.dimensionhandler.init_dims()
        try:
            G.world.savefile.load_world()
        except IOError:  # todo: add own exception class as IOError may be raised somewhere else in the script
            logger.println("failed to load world. data-fixer failed with NoDataFixerFoundException")
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:startmenu")
            return
        except:
            logger.write_exception("failed to load world")
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:startmenu")
            return
        for cx in range(-3, 4):
            for cz in range(-3, 4):
                self.status_table[(cx, cz)] = 0
                c = G.world.get_active_dimension().get_chunk(cx, cz, generate=False)
                """
                G.worldgenerationhandler.task_handler.schedule_invoke(
                    c, lambda: G.world.savefile.read("minecraft:chunk", dimension=G.world.active_dimension,
                                                     chunk=(cx, cz), immediate=False))
                c.generated = True"""
                G.world.savefile.read("minecraft:chunk", dimension=G.world.active_dimension, chunk=(cx, cz),
                                      immediate=False)
        G.worldgenerationhandler.enable_generation = True

    def on_deactivate(self):
        player = G.world.get_active_player()
        player.teleport(player.position, force_chunk_save_update=True)

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

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        if len(self.status_table) == 0:
            self.parts[1].text = "0%"
            self.parts[2].text = "0/0/0"
        else:
            self.parts[1].text = "{}%".format(round(self.calculate_percentage_of_progress() * 1000) / 10)
            self.parts[2].text = "{}/{}/{}".format(*G.worldgenerationhandler.task_handler.get_total_task_stats())

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            elif status == -1:
                color = (0, 255, 0)
            else:
                color = (136, 0, 255)
            mcpython.util.opengl.draw_rectangle((mx + cx * 10, my + cz * 10), (10, 10), color)


worldloading = None


def create():
    global worldloading
    worldloading = StateWorldLoading()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
