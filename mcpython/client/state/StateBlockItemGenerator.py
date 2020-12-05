"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from . import State, StatePartGame
from .ui import UIPartProgressBar
import mcpython.common.event.EventInfo
from mcpython import shared as G, logger
import pyglet
import os
import mcpython.ResourceLoader
import mcpython.common.item.Item
import mcpython.common.event.TickHandler
import PIL.Image, PIL.ImageDraw
import sys
import json
import mcpython.common.factory.ItemFactory
import mcpython.common.item.ItemHandler
import mcpython.common.mod.ModMcpython
import mcpython.client.state.StateModLoading
import psutil
import mcpython.client.gui.HoveringItemBox
import mcpython.client.rendering.model.ItemModel


class StateBlockItemGenerator(State.State):
    SETUP_TIME = 1
    CLEANUP_TIME = 1

    NAME = "minecraft:blockitemgenerator"

    def __init__(self):
        State.State.__init__(self)
        self.blockindex = 0
        self.tasks = []
        self.table = []
        self.last_image = None
        self.tries = 0
        self.failed_counter = 0

    def get_parts(self) -> list:
        kwargs = {}
        if G.prebuilding:
            kwargs["glcolor3d"] = (1.0, 1.0, 1.0)
        return [
            StatePartGame.StatePartGame(
                activate_physics=False,
                activate_mouse=False,
                activate_keyboard=False,
                activate_focused_block=False,
                clearcolor=(1.0, 1.0, 1.0, 0.0),
                activate_crosshair=False,
                activate_lable=False,
            ),
            UIPartProgressBar.UIPartProgressBar(
                (10, 10),
                (G.window.get_size()[0] - 20, 20),
                progress_items=len(G.registry.get_by_name("block").entries.values()),
                status=1,
                text="0/{}: {}".format(
                    len(G.registry.get_by_name("block").entries), None
                ),
            ),
            mcpython.client.state.StateModLoading.modloading.parts[3],
        ]

    def on_draw_2d_pre(self):
        self.parts[2].position = (10, G.window.get_size()[1] - 40)
        process = psutil.Process()
        with process.oneshot():
            self.parts[2].progress = process.memory_info().rss
        self.parts[2].text = "Memory usage: {}MB/{}MB ({}%)".format(
            self.parts[2].progress // 2 ** 20,
            self.parts[2].progress_max // 2 ** 20,
            round(self.parts[2].progress / self.parts[2].progress_max * 10000) / 100,
        )

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_resize(self, w, h):
        self.parts[1].size = (w - 20, 20)

    def on_activate(self):
        try:
            G.world.cleanup()
            G.dimensionhandler.init_dims()
            G.world.hide_faces_to_ungenerated_chunks = False
            G.tickhandler.enable_random_ticks = False
        except:
            logger.print_exception(
                "[FATAL] failed to open world for blockitemgenerator"
            )
            sys.exit(-1)
        self.tasks = list(G.registry.get_by_name("block").entries.keys())
        if not os.path.isdir(G.build + "/generated_items"):
            os.makedirs(G.build + "/generated_items")
        if not G.prebuilding:
            if os.path.exists(G.build + "/itemblockfactory.json"):
                with open(G.build + "/itemblockfactory.json", mode="r") as f:
                    self.table = json.load(f)
            else:  # make sure it is was reset
                self.table.clear()
            items = G.registry.get_by_name("item").entries
            for task in self.tasks[:]:
                if task in items:
                    self.tasks.remove(task)
        if len(self.tasks) == 0:  # we have nothing to do
            self.close()
            return
        self.parts[1].progress_max = len(self.tasks)
        self.parts[1].progress = 1
        G.window.set_size(800, 600)
        G.window.set_minimum_size(800, 600)
        G.window.set_maximum_size(800, 600)
        G.window.set_size(800, 600)
        G.world.get_active_player().position = (1.5, 2, 1.5)
        G.world.get_active_player().rotation = (-45, -45, 0)
        self.blockindex = -1
        try:
            blockinstance = G.world.get_active_dimension().add_block(
                (0, 0, 0), self.tasks[self.blockindex], block_update=False
            )
            if blockinstance.BLOCK_ITEM_GENERATOR_STATE is not None:
                blockinstance.set_model_state(blockinstance.BLOCK_ITEM_GENERATOR_STATE)
            blockinstance.face_state.update(redraw_complete=True)
        except ValueError:
            self.blockindex = 0
        # event.TickHandler.handler.bind(self.take_image, SETUP_TIME)
        mcpython.common.event.TickHandler.handler.enable_tick_skipping = False
        pyglet.clock.schedule_once(
            self.add_new_screen, (self.SETUP_TIME + self.CLEANUP_TIME) / 20
        )
        # event.TickHandler.handler.bind(self.add_new_screen, self.SETUP_TIME+self.CLEANUP_TIME)

    def on_deactivate(self):
        G.world.cleanup()
        with open(G.build + "/itemblockfactory.json", mode="w") as f:
            json.dump(self.table, f)
        G.registry.get_by_name("item").unlock()
        mcpython.common.factory.ItemFactory.ItemFactory.process()
        G.registry.get_by_name("item").lock()
        mcpython.common.item.ItemHandler.build()
        mcpython.common.item.ItemHandler.ITEM_ATLAS.load()
        G.window.set_minimum_size(1, 1)
        G.window.set_maximum_size(
            100000, 100000
        )  # only here for making resizing possible again
        mcpython.common.event.TickHandler.handler.enable_tick_skipping = True
        with open(G.build + "/info.json", mode="w") as f:
            json.dump({"finished": True}, f)
        mcpython.client.rendering.model.ItemModel.handler.bake()
        G.tickhandler.enable_random_ticks = True
        G.world.hide_faces_to_ungenerated_chunks = True
        G.window.set_fullscreen("--fullscreen" in sys.argv)
        G.eventhandler.call("stage:blockitemfactory:finish")

    def close(self):
        G.statehandler.switch_to("minecraft:startmenu")
        G.world.get_active_player().position = (0, 10, 0)
        G.world.get_active_player().rotation = (0, 0, 0)
        G.world.get_active_dimension().remove_block((0, 0, 0))
        self.last_image = None

    def add_new_screen(self, *args):
        self.blockindex += 1
        if self.blockindex >= len(self.tasks):
            self.close()
            return
        G.world.get_active_dimension().hide_block((0, 0, 0))
        try:
            blockinstance = G.world.get_active_dimension().add_block(
                (0, 0, 0), self.tasks[self.blockindex], block_update=False
            )
            if blockinstance.BLOCK_ITEM_GENERATOR_STATE is not None:
                blockinstance.set_model_state(blockinstance.BLOCK_ITEM_GENERATOR_STATE)
            blockinstance.face_state.update(redraw_complete=True)
        except ValueError:
            logger.print_exception(
                "[BLOCKITEMGENERATOR][ERROR] block '{}' can't be added to world. Failed with "
                "following exception".format(self.tasks[self.blockindex])
            )
            self.blockindex += 1
            pyglet.clock.schedule_once(self.add_new_screen, self.SETUP_TIME / 20)
            # event.TickHandler.handler.bind(self.add_new_screen, self.SETUP_TIME)
            return
        except:
            logger.println(self.tasks[self.blockindex])
            raise
        self.parts[1].progress = self.blockindex + 1
        self.parts[1].text = "{}/{}: {}".format(
            self.blockindex + 1, len(self.tasks), self.tasks[self.blockindex]
        )
        # todo: add states
        pyglet.clock.schedule_once(self.take_image, self.SETUP_TIME / 20)
        # event.TickHandler.handler.bind(self.take_image, self.SETUP_TIME)
        G.world.get_active_dimension().get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.blockindex >= len(self.tasks):
            return
        blockname = self.tasks[self.blockindex]
        file = "generated_items/{}.png".format("__".join(blockname.split(":")))
        try:
            pyglet.image.get_buffer_manager().get_color_buffer().save(
                G.build + "/" + file
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
        image.save(G.build + "/" + file)
        if image == self.last_image:
            self._error_counter(image, blockname)
            return
        self.last_image = image
        self.generate_item(blockname, file)
        pyglet.clock.schedule_once(self.add_new_screen, self.CLEANUP_TIME / 20)
        # event.TickHandler.handler.bind(self.add_new_screen, self.CLEANUP_TIME)

    def _error_counter(self, image, blockname):
        if self.tries >= 10:
            logger.println(
                "[BLOCKITEMGENERATOR][FATAL][ERROR] failed to generate block item for {}".format(
                    self.tasks[self.blockindex]
                )
            )
            self.last_image = image
            file = G.build + "/blockitemgenerator_fail_{}_of_{}.png".format(
                self.failed_counter, self.tasks[self.blockindex].replace(":", "__")
            )
            if image is not None:
                image.save(file)
                logger.println(
                    "[BLOCKITEMGENERATOR][FATAL][ERROR] image will be saved at {}".format(
                        file
                    )
                )
            file = "assets/missing_texture.png"  # use missing texture instead
            self.generate_item(blockname, file)
            mcpython.common.event.TickHandler.handler.bind(
                G.world.get_active_dimension().remove_block, 4, args=[(0, 0, 0)]
            )
            pyglet.clock.schedule_once(self.add_new_screen, 0.5)
            # event.TickHandler.handler.bind(self.add_new_screen, 10)
            self.blockindex += 1
            self.failed_counter += 1
            if self.failed_counter % 3 == 0 and self.SETUP_TIME <= 10:
                self.SETUP_TIME += 1
                self.CLEANUP_TIME += 1
            return
        pyglet.clock.schedule_once(self.take_image, 0.05)
        # event.TickHandler.handler.bind(self.take_image, 1)
        self.tries += 1

    def generate_item(self, blockname, file):
        if blockname in G.registry.get_by_name("item").entries:
            return
        self.table.append([blockname, file])
        obj = (
            mcpython.common.factory.ItemFactory.ItemFactory()
            .setDefaultItemFile(file)
            .setName(blockname)
            .setHasBlockFlag(True)
            .setToolTipRenderer(
                mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
            )
        )
        # block = G.world.get_active_dimension().get_block((0, 0, 0))
        # if type(block) != str and block is not None:
        #     block.modify_block_item(obj)
        obj.finish(task_list=True)
        model = mcpython.client.rendering.model.ItemModel.ItemModel(blockname)
        model.addTextureLayer(0, file)
        mcpython.client.rendering.model.ItemModel.handler.models[blockname] = model
        self.tries = 0
        self.SETUP_TIME = 1
        self.CLEANUP_TIME = 1


blockitemgenerator = None


def create():
    global blockitemgenerator
    blockitemgenerator = StateBlockItemGenerator()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)