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
import json
import os
import sys
import typing

import mcpython.client.gui.HoveringItemBox
import mcpython.client.rendering.model.ItemModel
import mcpython.client.state.StateModLoading
import mcpython.common.event.EventInfo
import mcpython.common.event.TickHandler
import mcpython.common.factory.ItemFactory
import mcpython.common.item.AbstractItem
import mcpython.common.item.ItemManager
import mcpython.common.mod.ModMcpython
import mcpython.ResourceLoader
import PIL.Image
import PIL.ImageDraw
import psutil
import pyglet
from mcpython import logger, shared
from mcpython.util.annotation import onlyInClient

from . import State, StatePartGame
from .ui import UIPartProgressBar


@onlyInClient()
class StateBlockItemGenerator(State.State):
    SETUP_TIME = 1
    CLEANUP_TIME = 1

    NAME = "minecraft:block_item_generator"

    def __init__(self):
        State.State.__init__(self)
        self.block_index = 0
        self.tasks: typing.List[str] = []
        self.table = []
        self.last_image = None
        self.tries = 0
        self.failed_counter = 0

    def get_parts(self) -> list:
        kwargs = {}
        if shared.invalidate_cache:
            kwargs["glcolor3d"] = (1.0, 1.0, 1.0)
        return [
            # We need to render stuff somewhere...
            StatePartGame.StatePartGame(
                activate_physics=False,
                activate_mouse=False,
                activate_keyboard=False,
                activate_focused_block=False,
                clear_color=(1.0, 1.0, 1.0, 0.0),
                activate_crosshair=False,
                activate_lable=False,
            ),
            # We want a progress bar to inform te user
            UIPartProgressBar.UIPartProgressBar(
                (10, 10),
                (shared.window.get_size()[0] - 20, 20),
                progress_items=len(
                    shared.registry.get_by_name("minecraft:block").entries.values()
                ),
                status=1,
                text="0/{}: {}".format(
                    len(shared.registry.get_by_name("minecraft:block").entries), None
                ),
            ),
            # the memory usage bar
            mcpython.client.state.StateModLoading.modloading.parts[3],
        ]

    def on_draw_2d_pre(self):
        # Update memory usage bar progress & text
        process = psutil.Process()
        with process.oneshot():
            self.parts[2].progress = process.memory_info().rss

        self.parts[2].text = "Memory usage: {}MB/{}MB ({}%)".format(
            self.parts[2].progress // 2 ** 20,
            self.parts[2].progress_max // 2 ** 20,
            round(self.parts[2].progress / self.parts[2].progress_max * 10000) / 100,
        )

    def bind_to_eventbus(self):
        # Helper code for event bus annotations
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_resize(self, w, h):
        # Update positions of the items
        self.parts[1].size = (w - 20, 20)
        self.parts[2].position = (10, h - 40)

    def activate(self):
        super().activate()

        # For faster access down the road
        world = shared.world
        item_registry = shared.registry.get_by_name("minecraft:item")

        # We want to work with BlockItems, so we need to unlock this registry again
        item_registry.unlock()

        # Clean up the system
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

        # Fetch the list of all blocks
        self.tasks = list(shared.registry.get_by_name("minecraft:block").entries.keys())
        os.makedirs(shared.build + "/generated_items", exist_ok=True)

        # If we do not do a all-redo, check what is needed
        if not shared.invalidate_cache:
            if os.path.exists(shared.build + "/item_block_factory.json"):
                with open(shared.build + "/item_block_factory.json", mode="r") as f:
                    self.table = json.load(f)
            else:  # make sure it is was reset
                self.table.clear()

            items = shared.registry.get_by_name("minecraft:item").entries
            for task in self.tasks[:]:
                if task in items:
                    self.tasks.remove(task)

        # Have we nothing to do -> We can stop here
        if len(self.tasks) == 0:
            self.close()
            return

        # We want to hide this error messages
        shared.model_handler.hide_blockstate_errors = True

        # Update the progress bar progress
        self.parts[1].progress_max = len(self.tasks)
        self.parts[1].progress = 1

        # Sets up the window, make it not resize-able
        window = shared.window
        window.set_fullscreen(False)
        window.set_size(800, 600)
        window.set_minimum_size(800, 600)
        window.set_maximum_size(800, 600)
        window.set_size(800, 600)

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
        mcpython.common.event.TickHandler.handler.enable_tick_skipping = False

        # And schedule the next add
        pyglet.clock.schedule_once(
            self.add_new_screen, (self.SETUP_TIME + self.CLEANUP_TIME) / 20
        )

    def deactivate(self):
        super().deactivate()

        # We want to enable this again
        shared.model_handler.hide_blockstate_errors = False

        # Clean up the world
        shared.world.cleanup()

        # dump our created data
        with open(shared.build + "/item_block_factory.json", mode="w") as f:
            json.dump(self.table, f)

        # baking the item textures needed
        mcpython.common.item.ItemManager.build()
        mcpython.common.item.ItemManager.ITEM_ATLAS.load()
        mcpython.client.rendering.model.ItemModel.handler.bake()

        logger.println("finished!")

        # only here for making resizing possible again
        window = shared.window
        window.set_minimum_size(1, 1)
        window.set_maximum_size(100000, 100000)

        with open(shared.build + "/info.json", mode="w") as f:
            json.dump({"finished": True}, f)

        # todo: Global variable, so user can toggle in-game
        window.set_fullscreen("--fullscreen" in sys.argv)

        shared.event_handler.call("stage:blockitemfactory:finish")

        mcpython.common.event.TickHandler.handler.enable_tick_skipping = True
        shared.world.hide_faces_to_not_generated_chunks = True

        item_registry = shared.registry.get_by_name("minecraft:item")
        item_registry.lock()

    def close(self):
        player = shared.world.get_active_player()
        player.position = (0, 10, 0)
        player.rotation = (0, 0, 0)
        player.dimension.remove_block((0, 0, 0))
        self.last_image = None

        shared.state_handler.switch_to("minecraft:startmenu")

    def add_new_screen(self, *args):
        self.block_index += 1

        dimension = shared.world.get_active_dimension()

        if self.block_index >= len(self.tasks):
            self.close()
            return

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

        self.parts[1].progress = self.block_index + 1
        self.parts[1].text = "{}/{}: {}".format(
            self.block_index + 1, len(self.tasks), self.tasks[self.block_index]
        )

        pyglet.clock.schedule_once(self.take_image, self.SETUP_TIME / 20)
        dimension.get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.block_index >= len(self.tasks):
            return

        blockname = self.tasks[self.block_index]
        file = "generated_items/{}.png".format("__".join(blockname.split(":")))
        try:
            pyglet.image.get_buffer_manager().get_color_buffer().save(
                shared.build + "/" + file
            )
        except PermissionError:
            logger.print_exception("FATAL DURING SAVING IMAGE FOR {}".format(blockname))
            pyglet.clock.schedule_once(self.take_image, 0.05)
            self._error_counter(None, blockname)
            return

        image: PIL.Image.Image = mcpython.ResourceLoader.read_image(file)
        if image.getbbox() is None or len(image.histogram()) <= 1:
            pyglet.clock.schedule_once(self.take_image, 0.05)
            # event.TickHandler.handler.bind(self.take_image, 1)
            self._error_counter(image, blockname)
            return

        image = image.crop(
            (240, 129, 558, 447)
        )  # todo: make dynamic based on window size
        image.save(shared.build + "/" + file)

        if image == self.last_image:
            self._error_counter(image, blockname)
            return

        self.last_image = image
        self.generate_item(blockname, file)
        pyglet.clock.schedule_once(self.add_new_screen, self.CLEANUP_TIME / 20)

    def _error_counter(self, image, blockname):
        if self.tries >= 10:
            logger.println(
                "[BLOCK ITEM GENERATOR][FATAL][ERROR] failed to generate block item for {}".format(
                    self.tasks[self.block_index]
                )
            )
            self.last_image = image
            file = shared.build + "/block_item_generator_fail_{}_of_{}.png".format(
                self.failed_counter, self.tasks[self.block_index].replace(":", "__")
            )
            if image is not None:
                image.save(file)
                logger.println(
                    "[BLOCK ITEM GENERATOR][FATAL][ERROR] image will be saved at {}".format(
                        file
                    )
                )
            file = "assets/missing_texture.png"  # use missing texture instead
            self.generate_item(blockname, file)
            mcpython.common.event.TickHandler.handler.bind(
                shared.world.get_active_dimension().remove_block, 4, args=[(0, 0, 0)]
            )
            pyglet.clock.schedule_once(self.add_new_screen, 0.5)
            # event.TickHandler.handler.bind(self.add_new_screen, 10)
            self.block_index += 1
            self.failed_counter += 1
            if self.failed_counter % 3 == 0 and self.SETUP_TIME <= 10:
                self.SETUP_TIME += 1
                self.CLEANUP_TIME += 1
            return

        pyglet.clock.schedule_once(self.take_image, 0.05)
        # event.TickHandler.handler.bind(self.take_image, 1)
        self.tries += 1

    def generate_item(self, blockname, file):
        if blockname in shared.registry.get_by_name("minecraft:item").entries:
            return
        self.table.append([blockname, file])
        obj = (
            mcpython.common.factory.ItemFactory.ItemFactory()
            .set_default_item_file(file)
            .set_name(blockname)
            .set_has_block_flag(True)
            .set_tool_tip_renderer(
                mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
            )
        )
        block = shared.world.get_active_dimension().get_block((0, 0, 0))
        if type(block) != str and block is not None:
            block.modify_block_item(obj)

        obj.finish()
        model = mcpython.client.rendering.model.ItemModel.ItemModel(blockname)
        model.addTextureLayer(0, file)
        mcpython.client.rendering.model.ItemModel.handler.models[blockname] = model
        self.tries = 0
        self.SETUP_TIME = 1
        self.CLEANUP_TIME = 1


block_item_generator = None


@onlyInClient()
def create():
    global block_item_generator
    block_item_generator = StateBlockItemGenerator()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
