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
import cProfile
import os
import random
import shutil
import sys
import typing

from pyglet.window import key

from mcpython import shared, logger
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
import mcpython.common.entity.PlayerEntity
from . import State
from mcpython.util.annotation import onlyInClient
import mcpython.server.worldgen.noise.NoiseManager
import mcpython.server.command.CommandParser


DEFAULT_GENERATION_CONFIG: typing.Dict[str, typing.Any] = {
    "world_config_name": "minecraft:default_overworld",
    "world_size": (5, 5),
    "seed_source": "minecraft:open_simplex_noise",
    "player_name": "unknown",
    "auto_gen_enabled": False,
    "world_barrier_enabled": False,
}


@onlyInClient()
class StateWorldGeneration(State.State):
    NAME = "minecraft:world_generation"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}
        self.profiler = cProfile.Profile()
        self.world_gen_config = {}

    def generate_world(self, config=None):
        if config is None:
            config = DEFAULT_GENERATION_CONFIG
            config["seed"] = random.randint(-1000000, 10000000)
        self.world_gen_config.update(config)
        shared.state_handler.switch_to(self.NAME)

    def generate_from_user_input(self, state=None):
        if state is None:
            state = shared.state_handler.states["minecraft:world_generation_config"]
        self.generate_world(
            {
                "world_config_name": state.get_world_config_name(),
                "world_size": state.get_world_size(),
                "seed_source": state.get_seed_source(),
                "seed": state.get_seed(),
                "player_name": state.get_player_name(),
                "auto_gen_enabled": state.is_auto_gen_enabled(),
                "world_barrier_enabled": state.is_world_gen_barrier_enabled(),
            }
        )

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
        shared.world_generation_handler.task_handler.process_tasks(timer=0.4)

        for chunk in self.status_table:
            c = shared.world.get_active_dimension().get_chunk(*chunk)
            if c not in shared.world_generation_handler.task_handler.chunks:
                self.status_table[chunk] = -1
            else:
                count = shared.world_generation_handler.task_handler.get_task_count_for_chunk(
                    c
                )
                self.status_table[chunk] = 1 / (count if count > 0 else 1)

        if len(shared.world_generation_handler.task_handler.chunks) == 0:
            shared.state_handler.switch_to("minecraft:game")
            import mcpython.common.data.ResourcePipe

            mcpython.common.data.ResourcePipe.handler.reload_content()
            self.finish()

    def activate(self):
        super().activate()
        if mcpython.common.config.ENABLE_PROFILER_GENERATION:
            self.profiler.enable()
        self.status_table.clear()

        if os.path.exists(shared.world.save_file.directory):
            # todo: simply rename world!
            logger.println("deleting old world...")
            shutil.rmtree(shared.world.save_file.directory)

        shared.dimension_handler.init_dims()

        shared.world_generation_handler.set_current_config(
            shared.world.get_dimension(0),
            self.world_gen_config["world_config_name"],
        )

        sx, sy = self.world_gen_config["world_size"]
        mcpython.server.worldgen.noise.NoiseManager.manager.default_implementation = (
            self.world_gen_config["seed_source"]
        )

        shared.world_generation_handler.enable_generation = True
        mcpython.server.worldgen.noise.NoiseManager.manager.set_noise_implementation()

        fx = sx // 2
        fy = sy // 2
        ffx = sx - fx
        ffy = sy - fy

        shared.event_handler.call("on_world_generation_prepared")

        seed = self.world_gen_config["seed"]
        shared.world.config["seed"] = seed
        shared.event_handler.call("seed:set")

        shared.event_handler.call("on_world_generation_started")

        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                shared.world_generation_handler.add_chunk_to_generation_list(
                    (cx, cz), force_generate=True
                )
                self.status_table[(cx, cz)] = 0

    def finish(self):
        # read in the config

        for pos in self.status_table:
            chunk = shared.world.get_active_dimension().get_chunk(*pos)
            chunk.is_ready = True
            chunk.visible = True

        shared.event_handler.call("on_game_generation_finished")
        logger.println("[WORLD GENERATION] finished world generation")
        player_name = self.world_gen_config["player_name"]
        if player_name == "":
            player_name = "unknown"
        if player_name not in shared.world.players:
            shared.world.add_player(player_name)

        # setup skin
        try:
            mcpython.util.getskin.download_skin(player_name, shared.build + "/skin.png")
        except ValueError:
            logger.print_exception(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    player_name
                )
            )
            try:
                mcpython.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                ).save(shared.build + "/skin.png")
            except:
                logger.print_exception(
                    "[FATAL] failed to load fallback skin. This is an serious issue!"
                )
                sys.exit(-1)

        if shared.IS_CLIENT:
            mcpython.common.entity.PlayerEntity.PlayerEntity.RENDERER.reload()

        # todo: this is also only client code
        shared.world.active_player = player_name
        shared.world.get_active_player().move_to_spawn_point()
        shared.world.config["enable_auto_gen"] = self.world_gen_config[
            "auto_gen_enabled"
        ]
        shared.world.config["enable_world_barrier"] = self.world_gen_config[
            "world_barrier_enabled"
        ]

        if shared.world_generation_handler.get_current_config(
            shared.world.get_dimension(0)
        ).GENERATES_START_CHEST:
            chunk = shared.world.get_active_dimension().get_chunk((0, 0))
            x, z = random.randint(0, 15), random.randint(0, 15)
            height = chunk.get_maximum_y_coordinate_from_generation(x, z)
            block_chest = shared.world.get_active_dimension().add_block(
                (x, height + 1, z), "minecraft:chest"
            )
            block_chest.loot_table_link = "minecraft:chests/spawn_bonus_chest"

        shared.event_handler.call("on_game_enter")

        # add surrounding chunks to load list
        shared.world.change_chunks(
            None,
            mcpython.util.math.position_to_chunk(
                shared.world.get_active_player().position
            ),
        )
        shared.world.save_file.save_world()

        # set player position
        player = shared.world.get_active_player()
        player.teleport(player.position, force_chunk_save_update=True)

        shared.world.world_loaded = True

        if (
            mcpython.common.config.SHUFFLE_DATA
            and mcpython.common.config.SHUFFLE_INTERVAL > 0
        ):
            shared.event_handler.call("data:shuffle:all")

        if mcpython.common.config.ENABLE_PROFILER_GENERATION:
            self.profiler.disable()
            self.profiler.print_stats(1)
            self.profiler.clear()

        # reload all the data-packs
        mcpython.common.DataPack.datapack_handler.reload()
        mcpython.common.DataPack.datapack_handler.try_call_function("#minecraft:load", mcpython.server.command.CommandParser.CommandExecutionEnvironment(dimension=shared.world.get_active_dimension()))
        shared.state_handler.switch_to("minecraft:gameinfo", immediate=False)

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d", self.on_draw_2d_post)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            shared.state_handler.switch_to("minecraft:startmenu")
            shared.tick_handler.schedule_once(shared.world.cleanup)
            logger.println("interrupted world generation by user")

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def on_draw_2d_post(self):
        wx, wy = shared.window.get_size()
        mx, my = wx // 2, wy // 2
        self.parts[1].text = "{}%".format(
            round(self.calculate_percentage_of_progress() * 1000) / 10
        )
        self.parts[2].text = "{}/{}/{}".format(
            *shared.world_generation_handler.task_handler.get_total_task_stats()
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


world_generation = None


@onlyInClient()
def create():
    global world_generation
    world_generation = StateWorldGeneration()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
