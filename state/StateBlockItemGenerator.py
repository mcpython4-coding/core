"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G
from pyglet.window import key
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

if not os.path.isdir(G.local+"/build/generated_items"): os.makedirs(G.local+"/build/generated_items")


SETUP_TIME = 1
CLEANUP_TIME = 1


class StateBlockItemGenerator(State.State):
    @staticmethod
    def get_name():
        return "minecraft:blockitemgenerator"

    def __init__(self):
        State.State.__init__(self)
        self.blockindex = 0
        G.registry.get_by_name("block").registered_objects.sort(key=lambda x: x.get_name())
        self.table = []

    def get_parts(self) -> list:
        kwargs = {}
        if "--rebuild" in sys.argv: kwargs["glcolor3d"] = (1., 1., 1.)
        return [StatePartGame.StatePartGame(activate_physics=False, activate_mouse=False, activate_keyboard=False,
                                            activate_focused_block=False, clearcolor=(1., 1., 1., 0.),
                                            activate_crosshair=False, activate_lable=False)]

    def on_activate(self):
        G.window.set_size(800, 600)
        G.window.set_minimum_size(800, 600)
        G.window.set_maximum_size(800, 600)
        G.window.set_size(800, 600)
        if "--rebuild" not in sys.argv:
            self.close()
            return
        G.window.position = (1.5, 2, 1.5)
        G.window.rotation = (-45, -45)
        G.world.get_active_dimension().add_block(
            (0, 0, 0), G.registry.get_by_name("block").registered_objects[0].get_name(), block_update=False)
        G.window.set_caption("generating block item images | block: {} | {} / {}".format(
            "null", 0, len(G.registry.get_by_name("block").registered_objects)
        ))
        self.blockindex = -1
        # event.TickHandler.handler.bind(self.take_image, SETUP_TIME)
        event.TickHandler.handler.bind(self.add_new_screen, SETUP_TIME+CLEANUP_TIME)

    def on_deactivate(self):
        G.world.cleanup()
        if "--rebuild" in sys.argv:
            with open(G.local+"/build/itemblockfactory.json", mode="w") as f:
                json.dump(self.table, f)
            item.ItemHandler.build()
        G.window.set_minimum_size(1, 1)
        G.window.set_maximum_size(100000, 100000)  # only here for making resizing possible again

    def close(self):
        G.statehandler.switch_to("minecraft:startmenu")
        G.window.position = (0, 10, 0)
        G.window.rotation = (0, 0)
        G.world.get_active_dimension().remove_block((0, 0, 0))
        G.window.set_caption("mcpython 4")

    def add_new_screen(self):
        self.blockindex += 1
        if self.blockindex >= len(G.registry.get_by_name("block").registered_objects):
            self.close()
            return
        # print(G.registry.get_by_name("block").registered_objects[self.blockindex].get_name())
        G.world.get_active_dimension().hide_block((0, 0, 0))
        G.world.get_active_dimension().add_block(
            (0, 0, 0), G.registry.get_by_name("block").registered_objects[self.blockindex].get_name(), block_update=False)
        G.window.set_caption("generating block item images | block: {} | {} / {}".format(
            G.registry.get_by_name("block").registered_objects[self.blockindex].get_name(), self.blockindex+1,
            len(G.registry.get_by_name("block").registered_objects)
        ))
        # todo: add states
        event.TickHandler.handler.bind(self.take_image, SETUP_TIME)
        G.world.get_active_dimension().get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.blockindex >= len(G.registry.get_by_name("block").registered_objects): return
        blockname = G.registry.get_by_name("block").registered_objects[self.blockindex].get_name()
        file = "build/generated_items/{}.png".format("__".join(blockname.split(":")))
        pyglet.image.get_buffer_manager().get_color_buffer().save(G.local + "/" + file)
        image: PIL.Image.Image = ResourceLocator.read(file, "pil")
        if image.getbbox() is None:
            event.TickHandler.handler.bind(self.take_image, 2)
            return
        image.crop((240, 129, 558, 447)).save(G.local + "/" + file)
        self.generate_item(blockname, file)
        event.TickHandler.handler.bind(self.add_new_screen, CLEANUP_TIME)

    def generate_item(self, blockname, file):
        self.table.append([blockname, file])
        factory.ItemFactory.ItemFactory().setDefaultItemFile(file).setName(blockname).setHasBlockFlag(True).finish()


blockitemgenerator = StateBlockItemGenerator()

