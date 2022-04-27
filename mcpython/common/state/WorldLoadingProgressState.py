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
import asyncio
import os

import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.common.mod.ModMcpython
import mcpython.common.state.ConfigBackgroundPart
import mcpython.common.state.ui.UIPartLabel
import mcpython.util.math
import mcpython.util.opengl
from mcpython import shared
from mcpython.engine import logger
from pyglet.window import key

from mcpython.engine.rendering.RenderingLayerManager import MIDDLE_GROUND
from mcpython.common.world.SaveFile import UnableToFixDataException
from . import AbstractState


class WorldLoadingProgress(AbstractState.AbstractState):
    NAME = "minecraft:world_loading"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)
        self.status_table = {}
        self.world_size = ((0, 0), (0, 0, 0, 0), 0)
        self.finished_chunks = 0

    async def load_or_generate(self, name: str):
        await shared.world.cleanup()
        shared.world.setup_by_filename(name)
        save_file = shared.world.save_file

        if not os.path.exists(save_file.directory):
            await shared.state_handler.states[
                "minecraft:world_generation"
            ].generate_world()
        else:
            await shared.state_handler.change_state("minecraft:world_loading")

    async def load_world_from(self, name: str):
        logger.println(f"[WORLD LOADING][INFO] starting loading world '{name}'")
        shared.world.setup_by_filename(name)
        await shared.state_handler.change_state("minecraft:world_loading")

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe(MIDDLE_GROUND.getRenderingEvent(), self.on_draw_2d_post)
        self.eventbus.subscribe("tickhandler:general", self.on_update)

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
        await shared.world_generation_handler.task_handler.process_tasks(timer=0.8)

        if shared.IS_CLIENT:
            for chunk in self.status_table:
                c = shared.world_generation_handler.task_handler.get_task_count_for_chunk(
                    shared.world.get_active_dimension().get_chunk(*chunk)
                )
                self.status_table[chunk] = 1 / c if c > 0 else -1

        if len(shared.world_generation_handler.task_handler.chunks) == 0:
            await shared.state_handler.change_state("minecraft:game")
            shared.world.world_loaded = True

            if (
                mcpython.common.config.SHUFFLE_DATA
                and mcpython.common.config.SHUFFLE_INTERVAL > 0
            ):
                await shared.event_handler.call_async("minecraft:data:shuffle:all")

        self.parts[1].text = "{}%".format(
            round(sum(self.status_table.values()) / len(self.status_table) * 1000) / 10
        )

    async def activate(self):
        await super().activate()

        # todo: add a check if we need this
        logger.println("[WORLD LOADING][INFO] reloading assets...")

        await shared.event_handler.call_async("data:reload:work")
        import mcpython.common.data.ResourcePipe

        await mcpython.common.data.ResourcePipe.handler.reload_content()

        shared.world_generation_handler.enable_generation = False
        self.status_table.clear()

        logger.println("[WORLD LOADING][INFO] initializing dimension info")
        shared.dimension_handler.init_dims()

        logger.println("[WORLD LOADING][INFO] preparing for world loading...")
        try:
            await shared.world.save_file.load_world_async()

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except UnableToFixDataException:  # todo: add own exception class as IOError may be raised somewhere else in the script
            logger.println(
                "Failed to load world. data-fixer Failed with NoDataFixerFoundException"
            )
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:start_menu")
            return

        except:
            logger.print_exception("Failed to load world; Failed in initial loading")
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:start_menu")
            return

        for cx in range(-3, 4):
            for cz in range(-3, 4):
                self.status_table[(cx, cz)] = 0
                # todo: fix bug: something is wrong here...
                # shared.world.savefile.read("minecraft:chunk", dimension=shared.world.get_active_player().dimension.id, chunk=(cx, cz),
                #                       immediate=False)
        shared.world_generation_handler.enable_generation = True

    async def deactivate(self):
        await super().deactivate()

        if shared.IS_CLIENT:
            player = await shared.world.get_active_player_async()
            player.teleport(player.position, force_chunk_save_update=True)

    async def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            await shared.state_handler.change_state("minecraft:start_menu")
            await shared.world.cleanup()

            logger.println("interrupted world loading by user")

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def on_draw_2d_post(self):
        wx, wy = shared.window.get_size()
        mx, my = wx // 2, wy // 2
        if len(self.status_table) == 0:
            self.parts[1].text = "0%"
            self.parts[2].text = "0/0/0"
        else:
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


world_loading = None


async def create():
    global world_loading
    world_loading = WorldLoadingProgress()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
