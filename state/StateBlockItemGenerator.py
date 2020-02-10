"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartProgressBar
import event.EventInfo
import globals as G
import pyglet
import os
import ResourceLocator
import item.Item
import event.TickHandler
import PIL.Image, PIL.ImageDraw
import sys
import json
import factory.ItemFactory
import item.ItemHandler
import mod.ModMcpython
import traceback
import logger
import state.StateModLoading
import psutil


class StateBlockItemGenerator(State.State):
    SETUP_TIME = 1
    CLEANUP_TIME = 1

    @staticmethod
    def get_name():
        return "minecraft:blockitemgenerator"

    def __init__(self):
        State.State.__init__(self)
        self.blockindex = 0
        G.registry.get_by_name("block").registered_objects.sort(key=lambda x: x.get_name())
        self.tasks = []
        self.table = []
        self.last_image = None
        self.tries = 0
        self.failed_counter = 0

    def get_parts(self) -> list:
        kwargs = {}
        if G.prebuilding: kwargs["glcolor3d"] = (1., 1., 1.)
        return [StatePartGame.StatePartGame(activate_physics=False, activate_mouse=False, activate_keyboard=False,
                                            activate_focused_block=False, clearcolor=(1., 1., 1., 0.),
                                            activate_crosshair=False, activate_lable=False),
                UIPartProgressBar.UIPartProgressBar((10, 10), (G.window.get_size()[0]-20, 20), progress_items=len(
                    G.registry.get_by_name("block").registered_objects), status=1, text="0/{}: {}".format(len(
                        G.registry.get_by_name("block").registered_objects), None)),
                state.StateModLoading.modloading.parts[3]]

    def on_draw_2d_pre(self):
        self.parts[2].position = (10, G.window.get_size()[1] - 40)
        process = psutil.Process()
        with process.oneshot():
            self.parts[2].progress = process.memory_info().rss
        self.parts[2].text = "Memory usage: {}MB/{}MB ({}%)".format(
            self.parts[2].progress // 2 ** 20, self.parts[2].progress_max // 2 ** 20,
            round(self.parts[2].progress / self.parts[2].progress_max * 10000) / 100)

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_resize(self, w, h):
        self.parts[1].size = (w-20, 20)

    def on_activate(self):
        G.tickhandler.enable_random_ticks = False
        self.tasks = [x.get_name() for x in G.registry.get_by_name("block").registered_objects]
        if not os.path.isdir(G.local + "/build/generated_items"): os.makedirs(G.local + "/build/generated_items")
        if not G.prebuilding:
            if os.path.exists(G.local+"/build/itemblockfactory.json"):
                with open(G.local+"/build/itemblockfactory.json", mode="r") as f:
                    self.table = json.load(f)
            else:  # make sure it is was reset
                self.table.clear()
            items = G.registry.get_by_name("item").get_attribute("items")
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
        G.window.position = (1.5, 2, 1.5)
        G.window.rotation = (-45, -45)
        self.blockindex = -1
        try:
            G.world.get_active_dimension().add_block((0, 0, 0), self.tasks[0], block_update=False)
        except ValueError:
            self.blockindex = 0
        # event.TickHandler.handler.bind(self.take_image, SETUP_TIME)
        event.TickHandler.handler.enable_tick_skipping = False
        event.TickHandler.handler.bind(self.add_new_screen, self.SETUP_TIME+self.CLEANUP_TIME)

    def on_deactivate(self):
        G.world.cleanup()
        with open(G.local+"/build/itemblockfactory.json", mode="w") as f:
            json.dump(self.table, f)
        factory.ItemFactory.ItemFactory.process()
        item.ItemHandler.build()
        item.ItemHandler.load_data(from_block_item_generator=True)
        G.window.set_minimum_size(1, 1)
        G.window.set_maximum_size(100000, 100000)  # only here for making resizing possible again
        event.TickHandler.handler.enable_tick_skipping = True
        with open(G.local + "/build/info.json", mode="w") as f:
            json.dump({"finished": True}, f)
        G.tickhandler.enable_random_ticks = True

    def close(self):
        G.statehandler.switch_to("minecraft:startmenu")
        G.window.position = (0, 10, 0)
        G.window.rotation = (0, 0)
        G.world.get_active_dimension().remove_block((0, 0, 0))
        self.last_image = None

    def add_new_screen(self):
        self.blockindex += 1
        if self.blockindex >= len(self.tasks):
            self.close()
            return
        G.world.get_active_dimension().hide_block((0, 0, 0))
        try:
            G.world.get_active_dimension().add_block((0, 0, 0), self.tasks[self.blockindex], block_update=False)
        except ValueError:
            logger.println("[BLOCKITEMGENERATOR][ERROR] block '{}' can't be added to world. Failed with "
                           "following exception".format(self.tasks[self.blockindex]))
            self.blockindex += 1
            event.TickHandler.handler.bind(self.add_new_screen, self.SETUP_TIME)
            traceback.print_exc()
            return
        self.parts[1].progress = self.blockindex+1
        self.parts[1].text = "{}/{}: {}".format(self.blockindex+1, len(self.tasks), self.tasks[self.blockindex])
        # todo: add states
        event.TickHandler.handler.bind(self.take_image, self.SETUP_TIME)
        G.world.get_active_dimension().get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.blockindex >= len(self.tasks): return
        blockname = self.tasks[self.blockindex]
        file = "build/generated_items/{}.png".format("__".join(blockname.split(":")))
        pyglet.image.get_buffer_manager().get_color_buffer().save(G.local + "/" + file)
        image: PIL.Image.Image = ResourceLocator.read(file, "pil")
        if image.getbbox() is None or len(image.histogram()) <= 1:
            event.TickHandler.handler.bind(self.take_image, 1)
            self._error_counter(image, blockname)
            return
        image = image.crop((240, 129, 558, 447))  # todo: make dynamic based on window size
        image.save(G.local + "/" + file)
        if image == self.last_image:
            self._error_counter(image, blockname)
            return
        self.last_image = image
        self.generate_item(blockname, file)
        event.TickHandler.handler.bind(self.add_new_screen, self.CLEANUP_TIME)

    def _error_counter(self, image, blockname):
        if self.tries >= 10:
            logger.println("[BLOCKITEMGENERATOR][FATAL][ERROR] failed to generate block item for {}".format(
                self.tasks[self.blockindex]))
            self.last_image = image
            file = G.local + "/tmp/blockitemgenerator_fail_{}_of_{}.png".format(
                self.failed_counter, self.tasks[self.blockindex].replace(":", "__"))
            image.save(file)
            logger.println("[BLOCKITEMGENERATOR][FATAL][ERROR] image will be saved at {}".format(file))
            file = "assets/missingtexture.png"  # use missing texture instead
            self.generate_item(blockname, file)
            event.TickHandler.handler.bind(G.world.get_active_dimension().remove_block, 4, args=[(0, 0, 0)])
            event.TickHandler.handler.bind(self.add_new_screen, 10)
            self.blockindex += 1
            self.failed_counter += 1
            if self.failed_counter % 3 == 0 and self.SETUP_TIME <= 10:
                self.SETUP_TIME += 1
                self.CLEANUP_TIME += 1
            return
        event.TickHandler.handler.bind(self.take_image, 1)
        self.tries += 1

    def generate_item(self, blockname, file):
        if blockname in G.registry.get_by_name("item").get_attribute("items"): return
        self.table.append([blockname, file])
        obj = factory.ItemFactory.ItemFactory().setDefaultItemFile(file).setName(blockname).setHasBlockFlag(True)
        block = G.world.get_active_dimension().get_block((0, 0, 0))
        if type(block) != str and block is not None: block.modify_block_item(obj)
        obj.finish()
        self.tries = 0


blockitemgenerator = None


def create():
    global blockitemgenerator
    blockitemgenerator = StateBlockItemGenerator()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

