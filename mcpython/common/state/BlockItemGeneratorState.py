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
__all__ = ["BlockItemGenerator", "block_item_generator"]

import asyncio
import json
import os
import sys
import typing

import mcpython.client.rendering.model.ItemModel as ItemModel
import mcpython.common.event.TickHandler as TickHandler
import mcpython.common.item.ItemManager as ItemManager
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.client.gui.HoveringItemBox import DEFAULT_BLOCK_ITEM_TOOLTIP
from mcpython.common.factory.ItemFactory import ItemFactory
from mcpython.common.mod.ModMcpython import minecraft
from mcpython.common.state.ModLoadingProgressState import mod_loading
from mcpython.engine import logger
from mcpython.engine.rendering.RenderingLayerManager import INTER_BACKGROUND
from mcpython.engine.ResourceLoader import read_image

from . import AbstractState, GameViewStatePart
from .ui import UIPartProgressBar
from .util import update_memory_usage_bar


class BlockItemGenerator(AbstractState.AbstractState):
    SETUP_TIME = 6
    CLEANUP_TIME = 4

    NAME = "minecraft:block_item_generator"

    def __init__(self):
        self.status_bar = None
        self.memory_bar = None

        AbstractState.AbstractState.__init__(self)

        # The current block number
        self.block_index: int = 0

        # The block names
        self.tasks: typing.List[str] = []

        # Temporary storage for the information in the json file for later runs
        self.table = []

        self.draw_calls_since_last_take = 0

    def create_state_parts(self) -> list:
        if not shared.IS_CLIENT:
            return []

        # We want a progress bar to inform te user
        self.status_bar = UIPartProgressBar.UIPartProgressBar(
            (10, 10),
            (shared.window.get_size()[0] - 20, 20),
            progress_items=len(
                shared.registry.get_by_name("minecraft:block").entries.values()
            ),
            status=1,
            text="0/{}: {}".format(
                len(shared.registry.get_by_name("minecraft:block").entries), None
            ),
        )

        self.memory_bar = mod_loading.memory_bar

        return [
            GameViewStatePart.GameView(
                activate_physics=False,
                activate_mouse=False,
                activate_keyboard=False,
                activate_focused_block=False,
                clear_color=(1.0, 1.0, 1.0, 0.0),
                activate_crosshair=False,
                activate_label=False,
            ),
            self.status_bar,
            self.memory_bar,
        ]

    def on_draw_2d_pre(self):
        update_memory_usage_bar(self.memory_bar)

        self.draw_calls_since_last_take += 1

    def bind_to_eventbus(self):
        # Helper code for event bus annotations
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe(
            INTER_BACKGROUND.getRenderingEvent(), self.on_draw_2d_pre
        )

    def on_resize(self, w, h):
        # Update positions of the items
        self.status_bar.size = (w - 20, 20)
        self.memory_bar.position = (10, h - 40)

    def tick(self, _):
        pass

    async def activate(self):
        await super().activate()

        logger.println("[BLOCK ITEM GENERATOR] starting up...")

        pyglet.clock.schedule_interval(self.tick, 1 / 400)

        world = shared.world
        item_registry = shared.registry.get_by_name("minecraft:item")

        # We want to work with BlockItems, so we need to unlock this registry again
        item_registry.unlock()

        # The world should be clean before we start work
        await self.clean_world(world)

        # Fetch the list of all blocks
        self.tasks = list(shared.registry.get_by_name("minecraft:block").entries.keys())

        os.makedirs(shared.build + "/generated_items", exist_ok=True)

        # If we do not do an all-redo, check what is needed
        if not shared.invalidate_cache:
            self.load_previous_data()

        # Remove the blocks we have items for
        # This is needed for the custom items (like redstone torch) that override this
        item_registry = shared.registry.get_by_name("minecraft:item")
        for task in self.tasks[:]:
            if task in item_registry:
                self.tasks.remove(task)

        # Have we nothing to do -> We can stop here
        if len(self.tasks) == 0:
            logger.println("[BLOCK ITEM GENERATOR] exiting, everything up-to-date")
            await self.close()
            return

        logger.println(f"[BLOCK ITEM GENERATOR] found {len(self.tasks)} block targets")

        # We want to hide this error messages
        # todo: add command line option to disable
        shared.model_handler.hide_blockstate_errors = True

        # Update the progress bar
        self.status_bar.progress_max = len(self.tasks)
        self.status_bar.progress = 1

        self.prepare_window()

        # Setup the player view, todo: make configurable by block model / state
        player = await world.get_active_player_async()
        player.position = (1.5, 2, 1.5)
        player.rotation = (-45, -45, 0)

        # Which block we are currently working on
        self.block_index = -1

        logger.println(f"[BLOCK ITEM GENERATOR] setting up initial target")

        try:
            instance = await world.get_active_dimension().add_block(
                (0, 0, 0), self.tasks[0], block_update=False
            )
            if instance.BLOCK_ITEM_GENERATOR_STATE is not None:
                await instance.set_model_state(instance.BLOCK_ITEM_GENERATOR_STATE)
            instance.face_info.update(redraw_complete=True)
        except:  # if the block is not working, use the next  lgtm [py/catch-base-exception]
            self.block_index = 0
            logger.print_exception(
                f"during adding first block to BlockItemGenerator (being {self.tasks[0]})"
            )

        # We do not want to skip ticks, as this would be bad here...
        TickHandler.handler.enable_tick_skipping = False

        # And schedule the next add
        pyglet.clock.schedule_once(
            self.add_new_screen, (self.SETUP_TIME + self.CLEANUP_TIME) / 20
        )

    def prepare_window(self):
        window = shared.window
        window.set_fullscreen(False)
        window.set_size(800, 600)
        window.set_minimum_size(800, 600)
        window.set_maximum_size(800, 600)
        window.set_size(800, 600)

    def load_previous_data(self):
        if os.path.exists(shared.build + "/item_block_factory.json"):
            with open(shared.build + "/item_block_factory.json", mode="r") as f:
                self.table = json.load(f)
        else:  # make sure it is reset
            self.table.clear()

        items = shared.registry.get_by_name("minecraft:item").entries
        for task in self.tasks[:]:
            if task in items:
                self.tasks.remove(task)

    async def clean_world(self, world):
        try:
            await world.cleanup()
            shared.dimension_handler.init_dims()
            world.hide_faces_to_not_generated_chunks = False
            shared.tick_handler.enable_random_ticks = False
        except:
            logger.print_exception(
                "failed to open world for block item generator; this is fatal; as such, the game closes now"
            )
            shared.window.close()
            sys.exit(-1)

    async def deactivate(self):
        await super().deactivate()

        logger.println("[BLOCK ITEM GENERATOR] closing Block Item Generator")

        pyglet.clock.unschedule(self.tick)

        # We want to enable this again
        shared.model_handler.hide_blockstate_errors = False

        # Clean up the world
        await shared.world.cleanup()

        # dump our created data
        with open(shared.build + "/item_block_factory.json", mode="w") as f:
            json.dump(self.table, f)

        logger.println("[BLOCK ITEM GENERATOR] baking items...")
        await self.bake_items()
        logger.println("[BLOCK ITEM GENERATOR] finished!")

        # only here for making resizing possible again
        window = shared.window
        window.set_minimum_size(1, 1)
        window.set_maximum_size(100000, 100000)

        with open(shared.build + "/info.json", mode="w") as f:
            json.dump({"finished": True}, f)

        # todo: Global variable, so user can toggle in-game
        window.set_fullscreen("--fullscreen" in sys.argv)

        await shared.event_handler.call_async("stage:blockitemfactory:finish")

        TickHandler.handler.enable_tick_skipping = True
        shared.world.hide_faces_to_not_generated_chunks = True

        item_registry = shared.registry.get_by_name("minecraft:item")
        item_registry.lock()

    async def bake_items(self):
        logger.println("[ITEM ENGINE] build()-ing ItemManager")
        await ItemManager.build()
        logger.println("[ITEM ENGINE] loading item atlas")
        ItemManager.ITEM_ATLAS.load()
        logger.println("[ITEM ENGINE] builtin item models")
        await ItemModel.handler.bake()

    async def close(self):
        player = await shared.world.get_active_player_async(create=False)

        if player is not None:
            player.position = (0, 10, 0)
            player.rotation = (0, 0, 0)
            await player.dimension.remove_block((0, 0, 0))

        if await shared.event_handler.call_cancelable_async(
            "stage_handler:loading2main_menu"
        ):
            await shared.state_handler.change_state("minecraft:start_menu")

    def add_new_screen(self, *args):
        self.block_index += 1

        if self.block_index >= len(self.tasks):
            asyncio.run(self.close())
            return

        dimension = shared.world.get_active_dimension()

        block = dimension.get_block((0, 0, 0))
        if block is not None:
            block.face_info.hide_all()

        try:
            instance = asyncio.run(
                dimension.add_block(
                    (0, 0, 0), self.tasks[self.block_index], block_update=False
                )
            )
            if instance.BLOCK_ITEM_GENERATOR_STATE is not None:
                asyncio.run(
                    instance.set_model_state(instance.BLOCK_ITEM_GENERATOR_STATE)
                )
            instance.face_info.update(redraw_complete=True)
        except:  # lgtm [py/catch-base-exception]
            logger.print_exception(
                "[BLOCK ITEM GENERATOR][ERROR] block '{}' can't be added to world. Failed with "
                "following exception".format(self.tasks[self.block_index])
            )

        self.status_bar.progress = self.block_index + 1
        self.status_bar.text = "{}/{}: {}".format(
            self.block_index + 1, len(self.tasks), self.tasks[self.block_index]
        )

        self.draw_calls_since_last_take = 0

        pyglet.clock.schedule_once(self.take_image, self.SETUP_TIME / 20)
        dimension.get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.draw_calls_since_last_take < 2:
            pyglet.clock.schedule_once(self.take_image, 1 / 20)
            return

        if self.block_index >= len(self.tasks):
            return

        block_name = self.tasks[self.block_index]
        file = "generated_items/{}.png".format("__".join(block_name.split(":")))
        try:
            pyglet.image.get_buffer_manager().get_color_buffer().save(
                shared.build + "/" + file
            )
        except PermissionError:
            logger.print_exception(
                "FATAL DURING SAVING IMAGE FOR {}".format(block_name)
            )
            self.block_index += 1
            pyglet.clock.schedule_once(self.add_new_screen, self.SETUP_TIME / 20)
            return

        image: PIL.Image.Image = asyncio.run(
            read_image(file)
        )

        image = image.crop(
            (240, 129, 558, 447)
        )  # todo: make dynamic based on window size
        image.save(shared.build + "/" + file)

        self.generate_item(block_name, file)
        pyglet.clock.schedule_once(self.add_new_screen, self.CLEANUP_TIME / 20)

    def generate_item(self, block_name: str, file: str):
        if block_name in shared.registry.get_by_name("minecraft:item").entries:
            return
        self.table.append([block_name, file])
        obj = (
            ItemFactory()
            .set_default_item_file(file)
            .set_name(block_name)
            .set_has_block_flag(True)
            .set_tool_tip_renderer(DEFAULT_BLOCK_ITEM_TOOLTIP)
        )
        block = shared.world.get_active_dimension().get_block((0, 0, 0))
        if type(block) != str and block is not None:
            block.modify_block_item(obj)

        obj.finish()

        model = ItemModel.ItemModel(block_name)
        model.addTextureLayer(0, file)
        ItemModel.handler.models[block_name] = model

        self.SETUP_TIME = 1
        self.CLEANUP_TIME = 1


block_item_generator = None


async def create():
    global block_item_generator
    block_item_generator = BlockItemGenerator()


minecraft.eventbus.subscribe("stage:states", create())
