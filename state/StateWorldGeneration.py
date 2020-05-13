"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import os
import random
import shutil

from pyglet.window import key

import ResourceLocator
import chat.DataPack
import globals as G
import logger
import mod.ModMcpython
import state.StatePartConfigBackground
import state.ui.UIPartLable
import util.getskin
import util.math
import util.opengl
import world.player
from . import State


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
        G.worldgenerationhandler.task_handler.process_tasks(timer=.4)
        for chunk in self.status_table:
            c = G.world.get_active_dimension().get_chunk(*chunk)
            if c not in G.worldgenerationhandler.task_handler.chunks:
                self.status_table[chunk] = -1
            else:
                count = G.worldgenerationhandler.task_handler.get_task_count_for_chunk(c)
                self.status_table[chunk] = 1 / (count if count > 0 else 1)
        if len(G.worldgenerationhandler.task_handler.chunks) == 0:
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
        # read in the config

        for pos in self.status_table:
            chunk = G.world.get_active_dimension().get_chunk(*pos)
            chunk.is_ready = True
            chunk.visible = True

        self = G.statehandler.states["minecraft:world_generation_config"]
        G.eventhandler.call("on_game_generation_finished")
        logger.println("[WORLDGENERATION] finished world generation")
        playername = self.parts[6].entered_text
        if playername == "": playername = "unknown"
        if playername not in G.world.players: G.world.add_player(playername)

        # setup skin
        try:
            util.getskin.download_skin(playername, G.local + "/build/skin.png")
        except ValueError:
            logger.write_exception(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(playername))
            ResourceLocator.read("assets/minecraft/textures/entity/steve.png", "pil").save(G.local + "/build/skin.png")
        world.player.Player.RENDERER.reload()
        G.world.active_player = playername
        G.world.get_active_player().position = (G.world.spawnpoint[0], util.math.get_max_y(G.world.spawnpoint),
                                                G.world.spawnpoint[1])
        G.world.config["enable_auto_gen"] = self.parts[2].textpages[self.parts[2].index] == "#*special.value.true*#"
        G.world.config["enable_world_barrier"] = \
            self.parts[3].textpages[self.parts[3].index] == "#*special.value.true*#"

        # reload all the data-packs
        chat.DataPack.datapackhandler.reload()
        chat.DataPack.datapackhandler.try_call_function("#minecraft:load")
        G.statehandler.switch_to("minecraft:gameinfo", immediate=False)

        # set spawn-point
        x, z = random.randint(0, 15), random.randint(0, 15)
        height = util.math.get_max_y((x, z))
        blockchest = G.world.get_active_dimension().add_block((x, height - 1, z), "minecraft:chest")
        blockchest.loot_table_link = "minecraft:chests/spawn_bonus_chest"
        G.eventhandler.call("on_game_enter")

        # add surrounding chunks to load list
        G.world.change_sectors(None, util.math.sectorize(G.world.get_active_player().position))
        G.world.savefile.save_world()

        # set player position
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
            logger.println("interrupted world generation by user")

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        self.parts[1].text = "{}%".format(round(sum(self.status_table.values())/len(self.status_table)*1000)/10)

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            elif status == -1:
                color = (0, 255, 0)
            else:
                color = (136, 0, 255)
            util.opengl.draw_rectangle((mx + cx * 10, my + cz * 10), (10, 10), color)


worldgeneration = None


def create():
    global worldgeneration
    worldgeneration = StateWorldGeneration()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
