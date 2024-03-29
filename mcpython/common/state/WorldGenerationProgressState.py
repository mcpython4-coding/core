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

import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.common.entity.PlayerEntity
import mcpython.common.mod.ModMcpython
import mcpython.common.state.ConfigBackgroundPart
import mcpython.common.state.ui.UIPartLabel
import mcpython.engine.ResourceLoader
import mcpython.server.command.CommandParser
import mcpython.server.worldgen.noise.NoiseManager
import mcpython.util.getskin
import mcpython.util.math
import mcpython.util.opengl
from mcpython import shared
from mcpython.engine import logger
from pyglet.window import key

from . import AbstractState

DEFAULT_GENERATION_CONFIG: typing.Dict[str, typing.Any] = {
    "world_config_name": "minecraft:default_overworld",
    "world_size": (5, 5),
    "seed_source": "minecraft:open_simplex_noise",
    "player_name": "unknown",
    "auto_gen_enabled": False,
    "world_barrier_enabled": False,
}


async def spawn_empty_world(player_name="unknown"):
    if player_name not in shared.world.players:
        await shared.world.add_player(player_name, dimension=0)

    # setup skin
    try:
        await mcpython.util.getskin.download_skin(
            player_name, shared.build + "/skin.png"
        )
    except ValueError:
        logger.print_exception(
            "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                player_name
            )
        )
        try:
            (
                await mcpython.engine.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                )
            ).save(shared.build + "/skin.png")
        except:
            logger.print_exception(
                "[FATAL] failed to load fallback skin. This is an serious issue!"
            )
            sys.exit(-1)

    await mcpython.common.entity.PlayerEntity.PlayerEntity.RENDERER.reload()

    shared.world.local_player = player_name
    shared.world.get_player_by_name(player_name).position = 0, 0, 0
    shared.world.get_player_by_name(player_name).set_gamemode(3)
    shared.world.config["enable_auto_gen"] = False
    shared.world.config["enable_world_barrier"] = False

    await shared.world.change_chunks_async(
        None,
        mcpython.util.math.position_to_chunk(
            shared.world.get_player_by_name(player_name).position
        ),
        dimension=shared.world.get_dimension(0),
    )


class WorldGenerationProgress(AbstractState.AbstractState):
    NAME = "minecraft:world_generation"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)
        self.status_table = {}
        self.profiler = cProfile.Profile()
        self.world_gen_config = {}

    async def generate_world(self, config=None):
        if config is None:
            config = DEFAULT_GENERATION_CONFIG
            config["seed"] = random.randint(-1000000, 10000000)
        self.world_gen_config.update(config)
        await shared.state_handler.change_state(self.NAME)

    async def generate_from_user_input(self, state=None):
        if state is None:
            state = shared.state_handler.states["minecraft:world_generation_config"]
        await self.generate_world(
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

    def create_state_parts(self) -> list:
        return [
            mcpython.common.state.ConfigBackgroundPart.ConfigBackground(),
            mcpython.common.state.ui.UIPartLabel.UIPartLabel(
                "0%",
                (0, 50),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
            mcpython.common.state.ui.UIPartLabel.UIPartLabel(
                "(0/0/0)",
                (0, 30),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
        ]

    async def on_update(self, dt):
        await shared.world_generation_handler.task_handler.process_tasks(timer=0.4)

        overworld = shared.world.get_dimension(0)

        for chunk in self.status_table:
            c = overworld.get_chunk(*chunk)
            if c not in shared.world_generation_handler.task_handler.chunks:
                self.status_table[chunk] = -1
            else:
                count = shared.world_generation_handler.task_handler.get_task_count_for_chunk(
                    c
                )
                self.status_table[chunk] = 1 / (count if count > 0 else 1)

        if len(shared.world_generation_handler.task_handler.chunks) == 0:
            await shared.state_handler.change_state("minecraft:game")
            import mcpython.common.data.ResourcePipe

            await mcpython.common.data.ResourcePipe.handler.reload_content()
            await self.finish()

    async def activate(self):
        await super().activate()
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

        await shared.event_handler.call_async("on_world_generation_prepared")

        seed = self.world_gen_config["seed"]
        shared.world.config["seed"] = seed
        await shared.event_handler.call_async("seed:set")

        await shared.event_handler.call_async("on_world_generation_started")

        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                shared.world_generation_handler.add_chunk_to_generation_list(
                    (cx, cz),
                    force_generate=True,
                    dimension=0,
                )
                self.status_table[(cx, cz)] = 0

    async def finish(self):
        # read in the config

        overworld = shared.world.get_dimension(0)

        for pos in self.status_table:
            chunk = overworld.get_chunk(*pos)
            chunk.is_ready = True
            chunk.visible = True

        await shared.event_handler.call_async("on_game_generation_finished")
        logger.println("[WORLD GENERATION] finished world generation")

        player_name = self.world_gen_config["player_name"]
        if player_name == "":
            player_name = "unknown"

        if player_name not in shared.world.players:
            await shared.world.add_player(player_name, dimension=0)

        # setup skin
        try:
            await mcpython.util.getskin.download_skin(
                player_name, shared.build + "/skin.png"
            )
        except ValueError:
            logger.print_exception(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    player_name
                )
            )
            try:
                (
                    await mcpython.engine.ResourceLoader.read_image(
                        "assets/minecraft/textures/entity/steve.png"
                    )
                ).save(shared.build + "/skin.png")
            except:
                logger.print_exception(
                    "[FATAL] failed to load fallback skin. This is an serious issue!"
                )
                sys.exit(-1)

        if shared.IS_CLIENT:
            await mcpython.common.entity.PlayerEntity.PlayerEntity.RENDERER.reload()

        # todo: this is also only client code
        shared.world.local_player = player_name
        shared.world.get_player_by_name(player_name).teleport_to_spawn_point()
        shared.world.config["enable_auto_gen"] = self.world_gen_config[
            "auto_gen_enabled"
        ]
        shared.world.config["enable_world_barrier"] = self.world_gen_config[
            "world_barrier_enabled"
        ]

        if shared.world_generation_handler.get_current_config(
            shared.world.get_dimension(0)
        ).GENERATES_START_CHEST:
            chunk = overworld.get_chunk((0, 0))
            x, z = random.randint(0, 15), random.randint(0, 15)
            height = chunk.get_maximum_y_coordinate_from_generation(x, z)
            block_chest = await overworld.add_block(
                (x, height + 1, z), "minecraft:chest"
            )
            block_chest.loot_table_link = "minecraft:chests/spawn_bonus_chest"

        await shared.event_handler.call_async("on_game_enter")

        # add surrounding chunks to load list
        await shared.world.change_chunks_async(
            None,
            mcpython.util.math.position_to_chunk(
                shared.world.get_player_by_name(player_name).position
            ),
            dimension=shared.world.get_dimension(0),
        )
        await shared.world.save_file.save_world_async()

        # set player position
        player = shared.world.get_player_by_name(player_name)
        player.teleport(player.position, force_chunk_save_update=True)

        shared.world.world_loaded = True

        if (
            mcpython.common.config.SHUFFLE_DATA
            and mcpython.common.config.SHUFFLE_INTERVAL > 0
        ):
            await shared.event_handler.call_async("minecraft:data:shuffle:all")

        # reload all the data-packs
        await mcpython.common.data.DataPacks.datapack_handler.reload()
        await mcpython.common.data.DataPacks.datapack_handler.try_call_function(
            "#minecraft:load",
            mcpython.server.command.CommandParser.CommandExecutionEnvironment(
                dimension=shared.world.get_dimension(0)
            ),
        )
        await shared.state_handler.change_state("minecraft:game", immediate=False)

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("tickhandler:general", self.on_update)

    async def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            await shared.state_handler.change_state("minecraft:start_menu")
            await shared.world.cleanup()
            logger.println(
                "Interrupted world generation by user; going back to start menu"
            )

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def create_state_renderer(self) -> typing.Any:
        from mcpython.client.state.WorldGenProgressRenderer import (
            WorldGenProgressRenderer,
        )

        return WorldGenProgressRenderer()


world_generation = None


async def create():
    global world_generation
    world_generation = WorldGenerationProgress()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
