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
import os
import shutil


class StateWorldGeneration(State.State):
    NAME = "minecraft:world_generation"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}

    def get_parts(self) -> list:
        return [state.StatePartConfigBackground.StatePartConfigBackground(),
                state.ui.UIPartLable.UIPartLable("0%", (0, 50), anchor_lable="MM", anchor_window="MD",
                                                 color=(255, 255, 255, 255))]

    def on_update(self, dt):
        start = time.time()
        flag = True
        while time.time() - start < 0.4 and flag:
            flag = G.worldgenerationhandler.process_one_generation_task(log_msg=False)
            if flag is None: flag = True
        for chunk in self.status_table:
            if G.world.get_active_dimension().get_chunk(*chunk, generate=False) in \
                    G.worldgenerationhandler.tasks_to_generate:
                self.status_table[chunk] = 0
                continue
            if chunk not in G.worldgenerationhandler.runtimegenerationcache[1]:
                self.status_table[chunk] = 6
                continue
            self.status_table[chunk] = G.worldgenerationhandler.runtimegenerationcache[1][chunk] + 1
        if len(G.worldgenerationhandler.tasks_to_generate) == len(G.worldgenerationhandler.runtimegenerationcache[0]) \
                == 0:
            G.statehandler.switch_to("minecraft:game")
            self.finish()

    def on_activate(self):
        if os.path.exists(G.world.savefile.directory):
            logger.println("deleting old world...")
            shutil.rmtree(G.world.savefile.directory)
        self.status_table.clear()
        G.dimensionhandler.init_dims()
        sx = G.statehandler.states["minecraft:world_generation_config"].parts[7].entered_text
        sx = 3 if sx == "" else int(sx)
        sy = G.statehandler.states["minecraft:world_generation_config"].parts[8].entered_text
        sy = 3 if sy == "" else int(sy)
        G.worldgenerationhandler.enable_generation = True
        fx = sx // 2
        fy = sy // 2
        ffx = sx - fx
        ffy = sy - fy
        G.eventhandler.call("on_world_generation_prepared")
        seed = G.statehandler.states["minecraft:world_generation_config"].parts[5].entered_text
        if seed != "":
            try:
                seed = int(seed)
            except ValueError:
                seed = int.from_bytes(seed.encode("UTF-8"), "big")
        else:
            seed = random.randint(-100000, 100000)
        G.world.config["seed"] = seed
        G.eventhandler.call("seed:set")
        G.eventhandler.call("on_world_generation_started")
        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                G.worldgenerationhandler.add_chunk_to_generation_list((cx, cz), force_generate=True, generate_add=False)
                self.status_table[(cx, cz)] = 0

    def finish(self):
        self = G.statehandler.states["minecraft:world_generation_config"]
        G.eventhandler.call("on_game_generation_finished")
        logger.println("[WORLDGENERATION] finished world generation")
        playername = self.parts[6].entered_text
        if playername not in G.world.players: G.world.add_player(playername)
        G.world.active_player = playername
        G.world.get_active_player().position = (G.world.spawnpoint[0], util.math.get_max_y(G.world.spawnpoint),
                                                G.world.spawnpoint[1])
        G.world.config["enable_auto_gen"] = self.parts[2].textpages[self.parts[2].index] == "#*special.value.true*#"
        G.world.config["enable_world_barrier"] = \
            self.parts[3].textpages[self.parts[3].index] == "#*special.value.true*#"
        if G.world.get_active_player().name == "": G.world.get_active_player().name = "unknown"
        chat.DataPack.datapackhandler.reload()
        chat.DataPack.datapackhandler.try_call_function("#minecraft:load")
        G.statehandler.switch_to("minecraft:gameinfo", immediate=False)
        G.eventhandler.call("on_game_enter")
        G.world.change_sectors(None, util.math.sectorize(G.world.get_active_player().position))  # add surrounding chunks to list
        G.world.savefile.save_world()

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d", self.on_draw_2d_post)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:startmenu")
            G.tickhandler.schedule_once(G.world.cleanup)
            logger.println("interrupted world generation by user")

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        self.parts[1].text = "{}%".format(round(list(
            self.status_table.values()).count(6)/len(self.status_table)*1000)/10)

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 6:
                factor = status / 6 * 255
                color = (factor, factor, factor)
            else:
                color = (136, 0, 255)
            util.opengl.draw_rectangle((mx+cx*10, my+cz*10), (10, 10), color)


worldgeneration = None


def create():
    global worldgeneration
    worldgeneration = StateWorldGeneration()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

