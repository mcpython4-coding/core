"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import world.player
import block.BlockHandler
import util.math
import world.Dimension
import world.Chunk
import pyglet
import time
import world.gen.WorldGenerationHandler


class World:
    def __init__(self):
        G.world = self
        self.player = world.player.Player("unknown")
        block.BlockHandler.load()
        self.dimensions = {}
        self.add_dimension(0, config={"configname": "default_overworld"})
        self.active_dimension = 0

    def get_active_dimension(self) -> world.Dimension.Dimension:
        return self.dimensions[self.active_dimension]

    def add_dimension(self, id, config={}) -> world.Dimension.Dimension:
        dim = self.dimensions[id] = world.Dimension.Dimension(self, id, genconfig=config)
        G.worldgenerationhandler.setup_dimension(dim, config)
        return dim

    def join_dimension(self, id):
        sector = util.math.sectorize(G.window.position)
        self.change_sectors(sector, None)
        self.active_dimension = id
        self.change_sectors(None, sector)

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = util.math.normalize((x, y, z))
            if key != previous and self.get_active_dimension().get_block(key):
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def show_sector(self, sector, immediate=False):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        self.get_active_dimension().get_chunk(*sector).show()

    def hide_sector(self, sector, immediate=False):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        self.get_active_dimension().get_chunk(*sector).hide()

    def change_sectors(self, before, after, immediate=False):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, z = before
                        before_set.add((x + dx, z + dz))
                    if after:
                        x, z = after
                        after_set.add((x + dx, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in hide:
            self.hide_sector(sector, immediate)
        for sector in show:
            self.show_sector(sector, immediate)

    def process_queue(self):
        dim: world.Dimension.Dimension = self.get_active_dimension()
        t = time.time()
        for chunk in list(dim.chunks.values()):
            for task in chunk.show_tasks:
                chunk._show_block(task)
                chunk.show_tasks.remove(task)
                if time.time() - t > 0.02:
                    return
            for task in chunk.hide_tasks:
                # print(task)
                chunk._hide_block(task)
                chunk.hide_tasks.remove(task)
                if time.time() - t > 0.02:
                    return
            for task in chunk.chunkgenerationtasks:
                task[0](*task[1], **task[2])
                chunk.chunkgenerationtasks.remove(task)
                if time.time() - t > 0.02:
                    return
            for position in list(chunk.blockmap.keys()):
                args, kwargs = chunk.blockmap[position]
                chunk.add_block(*args, **kwargs)
                del chunk.blockmap[position]
                if time.time() - t > 0.02:
                    return
            chunk.is_ready = \
                len(chunk.show_tasks) == len(chunk.hide_tasks) == len(chunk.chunkgenerationtasks) == len(chunk.blockmap)

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        dim: world.Dimension.Dimension = self.get_active_dimension()
        t = time.time()
        for chunk in list(dim.chunks.values()):
            for task in chunk.show_tasks:
                chunk._show_block(task, chunk.world[task])
            for task in chunk.hide_tasks:
                chunk._hide_block(task, chunk.world[task])
            while len(chunk.chunkgenerationtasks) > 0:
                task = chunk.chunkgenerationtasks.pop(0)
                task[0](*task[1], **task[2])
            for position in list(chunk.blockmap.keys()):
                args, kwargs = chunk.blockmap[position]
                chunk.add_block(*args, **kwargs)
            chunk.show_tasks = []
            chunk.hide_tasks = []
            chunk.blockmap = {}
            chunk.is_ready = True

    def cleanup(self, remove_dims=False):
        for dimension in self.dimensions.values():
            dimension: world.Dimension.Dimension
            for chunk in dimension.chunks.values():
                chunk.hide_all()
                chunk.world = {}
                chunk.is_ready = False
            dimension.chunks = {}
        if remove_dims:
            self.dimensions = {}

