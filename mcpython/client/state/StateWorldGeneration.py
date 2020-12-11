"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import cProfile
import os
import random
import shutil
import sys

from pyglet.window import key

from mcpython import shared as G, logger
import mcpython.ResourceLoader
import mcpython.common.DataPack
import mcpython.common.config
import mcpython.common.config
import mcpython.common.mod.ModMcpython
import mcpython.client.state.StatePartConfigBackground
import mcpython.client.state.ui.UIPartLabel
import mcpython.util.getskin
import mcpython.util.math
import mcpython.util.opengl
import mcpython.common.world.player
from . import State
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateWorldGeneration(State.State):
    NAME = "minecraft:world_generation"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}
        self.profiler = cProfile.Profile()

    def get_parts(self) -> list:
        return [
            mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground(),
            mcpython.client.state.ui.UIPartLabel.UIPartLabel(
                "0%",
                (0, 50),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
            mcpython.client.state.ui.UIPartLabel.UIPartLabel(
                "(0/0/0)",
                (0, 30),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
        ]

    def on_update(self, dt):
        G.world_generation_handler.task_handler.process_tasks(timer=0.4)
        for chunk in self.status_table:
            c = G.world.get_active_dimension().get_chunk(*chunk)
            if c not in G.world_generation_handler.task_handler.chunks:
                self.status_table[chunk] = -1
            else:
                count = G.world_generation_handler.task_handler.get_task_count_for_chunk(
                    c
                )
                self.status_table[chunk] = 1 / (count if count > 0 else 1)
        if len(G.world_generation_handler.task_handler.chunks) == 0:
            G.state_handler.switch_to("minecraft:game")
            G.event_handler.call("data:reload:work")
            self.finish()

    def on_activate(self):
        if mcpython.common.config.ENABLE_PROFILER_GENERATION:
            self.profiler.enable()
        if os.path.exists(G.world.savefile.directory):
            logger.println("deleting old world...")
            shutil.rmtree(G.world.savefile.directory)
        self.status_table.clear()
        G.dimension_handler.init_dims()
        sx = (
            G.state_handler.states["minecraft:world_generation_config"]
            .parts[7]
            .entered_text
        )
        sx = 3 if sx == "" else int(sx)
        sy = (
            G.state_handler.states["minecraft:world_generation_config"]
            .parts[8]
            .entered_text
        )
        sy = 3 if sy == "" else int(sy)
        G.world_generation_handler.enable_generation = True
        fx = sx // 2
        fy = sy // 2
        ffx = sx - fx
        ffy = sy - fy
        G.event_handler.call("on_world_generation_prepared")
        seed = (
            G.state_handler.states["minecraft:world_generation_config"]
            .parts[5]
            .entered_text
        )
        if seed != "":
            try:
                seed = int(seed)
            except ValueError:
                seed = int.from_bytes(seed.encode("UTF-8"), "big")
        else:
            seed = random.randint(-100000, 100000)
        G.world.config["seed"] = seed
        G.event_handler.call("seed:set")
        G.event_handler.call("on_world_generation_started")
        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                G.world_generation_handler.add_chunk_to_generation_list(
                    (cx, cz), force_generate=True
                )
                self.status_table[(cx, cz)] = 0

    def finish(self):
        master = self
        # read in the config

        for pos in self.status_table:
            chunk = G.world.get_active_dimension().get_chunk(*pos)
            chunk.is_ready = True
            chunk.visible = True

        self = G.state_handler.states["minecraft:world_generation_config"]
        G.event_handler.call("on_game_generation_finished")
        logger.println("[WORLDGENERATION] finished world generation")
        playername = self.parts[6].entered_text
        if playername == "":
            playername = "unknown"
        if playername not in G.world.players:
            G.world.add_player(playername)

        # setup skin
        try:
            mcpython.util.getskin.download_skin(playername, G.build + "/skin.png")
        except ValueError:
            logger.print_exception(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    playername
                )
            )
            try:
                mcpython.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                ).save(G.build + "/skin.png")
            except:
                logger.print_exception(
                    "[FATAL] failed to load fallback skin. This is an serious issue!"
                )
                sys.exit(-1)
        mcpython.common.world.player.Player.RENDERER.reload()
        G.world.active_player = playername
        G.world.get_active_player().set_to_spawn_point()
        G.world.config["enable_auto_gen"] = (
            self.parts[2].textpages[self.parts[2].index] == "#*special.value.true*#"
        )
        G.world.config["enable_world_barrier"] = (
            self.parts[3].textpages[self.parts[3].index] == "#*special.value.true*#"
        )

        # reload all the data-packs
        mcpython.common.DataPack.datapackhandler.reload()
        mcpython.common.DataPack.datapackhandler.try_call_function("#minecraft:load")
        G.state_handler.switch_to("minecraft:gameinfo", immediate=False)

        # set spawn-point
        chunk = G.world.get_active_dimension().get_chunk((0, 0))
        x, z = random.randint(0, 15), random.randint(0, 15)
        height = chunk.get_maximum_y_coordinate_from_generation(x, z)
        blockchest = G.world.get_active_dimension().add_block(
            (x, height + 1, z), "minecraft:chest"
        )
        blockchest.loot_table_link = "minecraft:chests/spawn_bonus_chest"
        G.event_handler.call("on_game_enter")

        # add surrounding chunks to load list
        G.world.change_chunks(
            None,
            mcpython.util.math.positionToChunk(G.world.get_active_player().position),
        )
        G.world.savefile.save_world()

        # set player position
        player = G.world.get_active_player()
        player.teleport(player.position, force_chunk_save_update=True)

        G.world.world_loaded = True

        if (
            mcpython.common.config.SHUFFLE_DATA
            and mcpython.common.config.SHUFFLE_INTERVAL > 0
        ):
            G.event_handler.call("data:shuffle:all")

        if mcpython.common.config.ENABLE_PROFILER_GENERATION:
            master.profiler.disable()
            master.profiler.print_stats(1)
            master.profiler.clear()

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d", self.on_draw_2d_post)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.state_handler.switch_to("minecraft:startmenu")
            G.tick_handler.schedule_once(G.world.cleanup)
            logger.println("interrupted world generation by user")

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        self.parts[1].text = "{}%".format(
            round(self.calculate_percentage_of_progress() * 1000) / 10
        )
        self.parts[2].text = "{}/{}/{}".format(
            *G.world_generation_handler.task_handler.get_total_task_stats()
        )

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            elif status == -1:
                color = (0, 255, 0)
            else:
                color = (136, 0, 255)
            mcpython.util.opengl.draw_rectangle(
                (mx + cx * 10, my + cz * 10), (10, 10), color
            )


worldgeneration = None


@onlyInClient()
def create():
    global worldgeneration
    worldgeneration = StateWorldGeneration()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
