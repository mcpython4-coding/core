"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import pyglet
import block.Block as Block
from util.math import *
import config
from typing import Dict, List
import util.math


class Chunk:
    attributes = {}

    @staticmethod
    def add_default_attribute(name, reference, default, authcode=None) -> int:
        if authcode is None: authcode = hash(name)
        Chunk.attributes[name] = (reference, default, authcode)
        return authcode

    def __init__(self, dimension, position):
        self.dimension = dimension
        self.position = position
        self.world = {}
        self.shown = {}
        self.show_tasks = []
        self.hide_tasks = []
        self.chunkgenerationtasks = []
        self.blockmap = {}  # an map with position -> [arguments: list, optional_arguments: kwargs] generation code
        self.is_ready = False  # todo: change to False after new world gen is introduced
        self.visible = False
        self.loaded = True
        self.attr = {}
        for attr in self.attributes.keys():
            self.attr[attr] = self.attributes[attr][1]

    def set_value(self, name, value, authcode):
        if authcode != self.attributes[name][2]:
            raise ValueError("not able to set value. protection is not uncoverable")
        self.attr[name] = value

    def get_value(self, name):
        return self.attr[name]

    def draw(self):
        if not self.is_ready or len(self.chunkgenerationtasks) > 0: return
        if not self.visible: return
        if not self.loaded:
            # todo: load chunk
            return

    def exposed(self, position):
        """ Returns False is given `position` should be hidden, True otherwise.

        """
        x, y, z = position
        for i, (dx, dy, dz) in enumerate(config.FACES):
            pos = (x + dx, y + dy, z + dz)
            block = self.dimension.get_block(pos)
            if not (block and (block.is_solid_side(config.FACE_NAMES[i]) if type(block) != str else
                               G.registry.get_by_name("block").get_attribute("blocks")[block].is_solid_side(None, config.FACE_NAMES[i]))):
                return True
        return False

    def add_add_block_gen_task(self, position: tuple, block_name: str, immediate=True, block_update=True, args=[],
                               kwargs={}):
        self.blockmap[position] = ([position, block_name], {"immediate": immediate, "block_update": block_update,
                                                            "args": args, "kwargs": kwargs})

    def is_position_blocked(self, position):
        return position in self.world or position in self.blockmap

    def add_block(self, position: tuple, block_name: str, immediate=True, block_update=True, args=[], kwargs={}):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        block_name : the name of the block to add
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position != util.math.normalize(position):
            raise ValueError("position {} is no valid block position".format(position))
        # print("adding", block_name, "at", position)
        if position in self.world:
            self.remove_block(position, immediate=immediate, block_update=block_update)
        if position[1] < 0 or position[1] > 255: return
        if block_name in [None, "air", "minecraft:air"]: return
        if issubclass(type(block_name), Block.Block):
            blockobj = block_name
            blockobj.position = position
        else:
            blockobj = G.registry.get_by_name("block").get_attribute("blocks")[block_name](position, *args, **kwargs)
        self.world[position] = blockobj
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            if block_update:
                self.on_block_updated(position)
            self.check_neighbors(position)

    def on_block_updated(self, position):
        x, y, z = position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if [dx, dy, dz].count(0) >= 2:
                        b: Block.Block = self.dimension.get_block((x+dx, y+dy, z+dz))
                        if b and type(b) != str:
                            b.on_block_update()

    def remove_block(self, position, immediate=True, block_update=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        # print("removing", self.world[position] if position in self.world else None, "at", position)
        if position not in self.world: return
        if issubclass(type(position), Block.Block):
            position = position.position
        self.world[position].on_delete()
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            if block_update:
                self.on_block_updated(position)
            self.check_neighbors(position)
        del self.world[position]

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in config.FACES:
            key = (x + dx, y + dy, z + dz)
            b = self.dimension.get_block(key)
            chunk = self.dimension.get_chunk_for_position(key, generate=False)
            if not b:
                continue
            if self.exposed(key):
                if key not in chunk.shown:
                    chunk.show_block(key)
            else:
                if key in chunk.shown:
                    chunk.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        if type(position) == Block.Block:
            position = position.position
        if position not in self.world: return
        if position in self.shown:
            self.hide_block(position)
        self.shown[position] = []
        if immediate:
            self._show_block(position, self.world[position])
        else:
            if position in self.hide_tasks:
                self.hide_tasks.remove(position)
                return
            self.show_tasks.append(position)

    def _show_block(self, position, block):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        block: the blockinstance to show

        """
        # print("showing", position)
        self.shown[position] = G.modelhandler.add_to_batch(block, position, self.dimension.batches)
        # print(self.world[position], self.shown[position])

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        if type(position) == Block.Block:
            position = position.position
        if position not in self.shown: return
        if immediate:
            self._hide_block(position)
        else:
            if position in self.show_tasks:
                self.show_tasks.remove(position)
                return
            self.hide_tasks.append(position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        # print("hiding", self.tmpworld[position], "at", position, "with", self.tmpworld[position].shown_data)
        [x.delete() for x in self.shown[position]]
        del self.shown[position]

    def show(self):
        self.visible = True
        self.update_visable(hide=False)

    def hide(self):
        self.visible = False
        self.hide_all()

    def update_visable_block(self, position, hide=True):
        if not self.exposed(position):
            self.hide_block(position)
        elif hide:
            self.show_block(position)

    def update_visable(self, hide=True):
        for position in self.world.keys():
            self.chunkgenerationtasks.append([self.update_visable_block, [position], {"hide": hide}])

    def hide_all(self, immediate=True):
        for position in self.shown.copy():
            self.hide_block(position, immediate=immediate)

    def get_block(self, position):
        return self.blockmap[position][0][1] if position in self.blockmap else (self.world[position] if position in
                                                                                self.world else None)

