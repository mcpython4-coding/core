"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State
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


class StateWorldGeneration(State.State):
    NAME = "minecraft:world_generation"

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [state.StatePartConfigBackground.StatePartConfigBackground()]

    def on_update(self, dt):
        start = time.time()
        flag = True
        while time.time() - start < 0.4 and flag:
            flag = G.worldgenerationhandler.process_one_generation_task()
            if flag is None: flag = True
        if len(G.worldgenerationhandler.tasks_to_generate) == len(G.worldgenerationhandler.runtimegenerationcache[0]) \
                == 0:
            G.statehandler.switch_to("minecraft:game")

    def on_activate(self):
        G.world.cleanup(remove_dims=True)
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
        G.eventhandler.call("on_world_generation_started")
        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                G.worldgenerationhandler.add_chunk_to_generation_list((cx, cz), force_generate=True)

    def on_deactivate(self):
        self = G.statehandler.states["minecraft:world_generation_config"]
        G.eventhandler.call("on_game_generation_finished")
        logger.println("[WORLDGENERATION] finished world generation")
        G.player.position = (G.world.spawnpoint[0], util.math.get_max_y(G.world.spawnpoint), G.world.spawnpoint[1])
        G.world.config["enable_auto_gen"] = self.parts[2].textpages[self.parts[2].index] == "#*special.value.true*#"
        G.world.config["enable_world_barrier"] = \
            self.parts[3].textpages[self.parts[3].index] == "#*special.value.true*#"
        G.player.name = self.parts[6].entered_text
        if G.player.name == "": G.player.name = "unknown"
        chat.DataPack.datapackhandler.reload()
        chat.DataPack.datapackhandler.try_call_function("#minecraft:load")
        G.statehandler.switch_to("minecraft:gameinfo", immediate=False)
        G.eventhandler.call("on_game_enter")
        G.world.change_sectors(None, util.math.sectorize(G.player.position))  # add surrounding chunks to list

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:start_menu")

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1., 1., 1., 1.)


worldgeneration = None


def create():
    global worldgeneration
    worldgeneration = StateWorldGeneration()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

