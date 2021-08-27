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

import json
import os
import sys
import typing

from mcpython.client.gui.HoveringItemBox import DEFAULT_BLOCK_ITEM_TOOLTIP
import mcpython.client.rendering.model.ItemModel as ItemModel
from mcpython.client.state.ModLoadingProgressState import mod_loading
import mcpython.common.event.TickHandler as TickHandler
from mcpython.common.factory.ItemFactory import ItemFactory
import mcpython.common.item.ItemManager as ItemManager
from mcpython.common.mod.ModMcpython import minecraft
from mcpython.engine.ResourceLoader import read_image
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.engine import logger
from mcpython.util.annotation import onlyInClient

from . import AbstractState, GameViewStatePart
from .ui import UIPartProgressBar
from .util import update_memory_usage_bar


@onlyInClient()
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

        self.got_draw_call = False

    def get_parts(self) -> list:
        kwargs = {}
        if shared.invalidate_cache:
            kwargs["glcolor3d"] = (1.0, 1.0, 1.0)

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

        self.got_draw_call = True

    def bind_to_eventbus(self):
        # Helper code for event bus annotations
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_resize(self, w, h):
        # Update positions of the items
        self.status_bar.size = (w - 20, 20)
        self.memory_bar.position = (10, h - 40)

    def activate(self):
        super().activate()

        world = shared.world
        item_registry = shared.registry.get_by_name("minecraft:item")

        # We want to work with BlockItems, so we need to unlock this registry again
        item_registry.unlock()

        # The world should be clean before we start work
        self.clean_world(world)

        # Fetch the list of all blocks
        self.tasks = list(shared.registry.get_by_name("minecraft:block").entries.keys())

        os.makedirs(shared.build + "/generated_items", exist_ok=True)

        # If we do not do a all-redo, check what is needed
        if not shared.invalidate_cache:
            self.load_previous_data()

        # Have we nothing to do -> We can stop here
        if len(self.tasks) == 0:
            self.close()
            return

        # We want to hide this error messages
        # todo: add command line option to disable
        shared.model_handler.hide_blockstate_errors = True

        # Update the progress bar progress
        self.status_bar.progress_max = len(self.tasks)
        self.status_bar.progress = 1

        self.prepare_window()

        # Setup the player view, todo: make configurable by block
        player = world.get_active_player()
        player.position = (1.5, 2, 1.5)
        player.rotation = (-45, -45, 0)

        # Which block we are currently working on
        self.block_index = -1

        try:
            instance = world.get_active_dimension().add_block(
                (0, 0, 0), self.tasks[0], block_update=False
            )
            if instance.BLOCK_ITEM_GENERATOR_STATE is not None:
                instance.set_model_state(instance.BLOCK_ITEM_GENERATOR_STATE)
            instance.face_state.update(redraw_complete=True)
        except ValueError:  # if the block is not working, use the next
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
        else:  # make sure it is was reset
            self.table.clear()
        items = shared.registry.get_by_name("minecraft:item").entries
        for task in self.tasks[:]:
            if task in items:
                self.tasks.remove(task)

    def clean_world(self, world):
        try:
            world.cleanup()
            shared.dimension_handler.init_dims()
            world.hide_faces_to_not_generated_chunks = False
            shared.tick_handler.enable_random_ticks = False
        except:
            logger.print_exception(
                "failed to open world for block item generator; this is fatal; as such, the game closes now"
            )
            shared.window.close()
            sys.exit(-1)

    def deactivate(self):
        super().deactivate()

        # We want to enable this again
        shared.model_handler.hide_blockstate_errors = False

        # Clean up the world
        shared.world.cleanup()

        # dump our created data
        with open(shared.build + "/item_block_factory.json", mode="w") as f:
            json.dump(self.table, f)

        self.bake_items()

        logger.println("[BLOCK ITEM GENERATOR] finished!")

        # only here for making resizing possible again
        window = shared.window
        window.set_minimum_size(1, 1)
        window.set_maximum_size(100000, 100000)

        with open(shared.build + "/info.json", mode="w") as f:
            json.dump({"finished": True}, f)

        # todo: Global variable, so user can toggle in-game
        window.set_fullscreen("--fullscreen" in sys.argv)

        shared.event_handler.call("stage:blockitemfactory:finish")

        TickHandler.handler.enable_tick_skipping = True
        shared.world.hide_faces_to_not_generated_chunks = True

        item_registry = shared.registry.get_by_name("minecraft:item")
        item_registry.lock()

    def bake_items(self):
        ItemManager.build()
        ItemManager.ITEM_ATLAS.load()
        ItemModel.handler.bake()

    def close(self):
        player = shared.world.get_active_player()
        player.position = (0, 10, 0)
        player.rotation = (0, 0, 0)
        player.dimension.remove_block((0, 0, 0))

        shared.state_handler.change_state("minecraft:start_menu")

    def add_new_screen(self, *args):
        self.block_index += 1

        if self.block_index >= len(self.tasks):
            self.close()
            return

        dimension = shared.world.get_active_dimension()

        block = dimension.get_block((0, 0, 0))
        if block is not None:
            block.face_state.hide_all()

        try:
            instance = dimension.add_block(
                (0, 0, 0), self.tasks[self.block_index], block_update=False
            )
            if instance.BLOCK_ITEM_GENERATOR_STATE is not None:
                instance.set_model_state(instance.BLOCK_ITEM_GENERATOR_STATE)
            instance.face_state.update(redraw_complete=True)
        except ValueError:
            logger.print_exception(
                "[BLOCK ITEM GENERATOR][ERROR] block '{}' can't be added to world. Failed with "
                "following exception".format(self.tasks[self.block_index])
            )
            self.block_index += 1
            pyglet.clock.schedule_once(self.add_new_screen, self.SETUP_TIME / 20)
            return
        except:
            logger.println(self.tasks[self.block_index])
            raise

        self.status_bar.progress = self.block_index + 1
        self.status_bar.text = "{}/{}: {}".format(
            self.block_index + 1, len(self.tasks), self.tasks[self.block_index]
        )

        self.got_draw_call = False

        pyglet.clock.schedule_once(self.take_image, self.SETUP_TIME / 20)
        dimension.get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if not self.got_draw_call:
            pyglet.clock.schedule_once(self.take_image, 1/20)
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

        image: PIL.Image.Image = read_image(file)

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
            .set_tool_tip_renderer(
                DEFAULT_BLOCK_ITEM_TOOLTIP
            )
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


@onlyInClient()
def create():
    global block_item_generator
    block_item_generator = BlockItemGenerator()


minecraft.eventbus.subscribe("stage:states", create)
