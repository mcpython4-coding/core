"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import pyglet
import block.Block
from util.math import *
import config
from typing import Dict, List


class Chunk:
    def __init__(self, dimension, position):
        self.dimension = dimension
        self.position = position
        self.world = {}
        self.tmpworld = {}
        self.shown = {}
        self.show_tasks = []
        self.hide_tasks = []
        self.is_ready = True  # todo: change to False after new world gen is introduced
        self.visible = False
        self.loaded = True
        # normal batch
        self.batches = [pyglet.graphics.Batch()]

    def draw(self):
        if not self.is_ready: return
        if not self.visible: return
        if not self.loaded:
            # todo: load chunk
            return
        self.batches[0].draw()

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in config.FACES:
            # todo: add solid-check
            pos = (x + dx, y + dy, z + dz)
            chunk = self.dimension.get_chunk_for_position(pos, generate=False)
            if pos not in chunk.world:
                return True
        return False

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
        # print("adding", block_name, "at", position)
        if position in self.world:
            self.remove_block(position, immediate=immediate, block_update=block_update)
        if position[1] < 0 or position[1] > 255: return
        if block_name in [None, "air", "minecraft:air"]: return
        if issubclass(type(block_name), block.Block.Block):
            blockobj = block_name
            blockobj.position = position
        else:
            blockobj = G.blockhandler.blocks[block_name](position, *args, **kwargs)
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
                        b: block.Block.Block = self.dimension.get_block((x+dx, y+dy, z+dz))
                        if b:
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
        if issubclass(type(position), block.Block.Block):
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
        if type(position) == block.Block.Block:
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
        self.shown[position] = G.modelloader.show_block(self.batches, position, block.get_model_name())
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
        if type(position) == block.Block.Block:
            position = position.position
        if position not in self.shown: return
        self.tmpworld[position] = self.world[position]
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
        del self.tmpworld[position]

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def update_visable(self, immediate=True):
        for position in self.world.keys():
            if not self.exposed(position):
                self.hide_block(position, immediate=immediate)
            else:
                self.show_block(position, immediate=immediate)

    def hide_all(self, immediate=True):
        for position in self.shown.copy():
            self.hide_block(position, immediate=immediate)

