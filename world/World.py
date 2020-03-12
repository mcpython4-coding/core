"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import world.player
import block.BlockHandler
import util.math
import world.Dimension
import world.Chunk
import pyglet
import time
import world.gen.WorldGenerationHandler
import state.StatePartGame
import gui.Inventory
import random
import world.GameRule
import config
import storage.SaveFile


class World:
    def __init__(self, filename=None):
        G.world = self
        self.spawnpoint = (random.randint(0, 15), random.randint(0, 15))
        self.dimensions = {}
        self.add_dimension(0, "minecraft:overworld", {'configname': None})
        self.active_dimension = 0
        self.config = {}  # contains: seed
        self.gamerulehandler = None
        self.reset_config()
        self.CANCEL_DIM_CHANGE = False
        self.hide_faces_to_ungenerated_chunks = True
        self.filename = "tmp" if filename is None else filename
        self.savefile = storage.SaveFile.SaveFile(self.filename)

        self.players = {}  # when in an network, stores an reference to all other players
        self.add_player("unknown", add_inventories=False)
        self.active_player = "unknown"

    def add_player(self, name, add_inventories=True):
        self.players[name] = world.player.Player(name)
        if add_inventories:
            self.players[name].create_inventories()

    def get_active_player(self):
        return self.players[self.active_player]

    def reset_config(self):
        self.config = {"enable_auto_gen": False, "enable_world_barrier": False}
        G.eventhandler.call("world:reset_config")
        self.gamerulehandler = world.GameRule.GameRuleHandler(self)
        self.hide_faces_to_ungenerated_chunks = True

    def get_active_dimension(self) -> world.Dimension.Dimension:
        if self.active_dimension not in self.dimensions: return
        return self.dimensions[self.active_dimension]

    def add_dimension(self, id, name, config={}) -> world.Dimension.Dimension:
        dim = self.dimensions[id] = world.Dimension.Dimension(self, id, name, genconfig=config)
        G.worldgenerationhandler.setup_dimension(dim, config)
        return dim

    def join_dimension(self, id, save_current=True):
        self.CANCEL_DIM_CHANGE = False
        G.eventhandler.call("dimension:chane:pre", id)
        if self.CANCEL_DIM_CHANGE: return
        sector = util.math.sectorize(G.world.get_active_player().position)
        self.change_sectors(sector, None)
        self.active_dimension = id
        self.change_sectors(None, sector)
        G.eventhandler.call("dimension:chane:post", id)

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
        m = G.world.gamerulehandler.table["hitTestSteps"].status.status
        x, y, z = position
        dx, dy, dz = vector
        dx /= m
        dy /= m
        dz /= m
        previous = None
        for _ in range(max_distance * m):
            key = util.math.normalize((x, y, z))
            blocki = self.get_active_dimension().get_block(key)
            if blocki and type(blocki) != str and blocki.get_view_bbox().test_point_hit((x, y, z), blocki.position):
                return key, previous, (x, y, z)
            if key != previous:
                previous = key
            x += dx
            y += dy
            z += dz
        return None, None, None

    def show_sector(self, sector, immediate=False):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        self.get_active_dimension().get_chunk(*sector, generate=False).show()

    def hide_sector(self, sector, immediate=False):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        self.get_active_dimension().get_chunk(*sector, generate=False).hide()

    def change_sectors(self, before, after, immediate=False, generate_chunks=True, load_immediate=False):
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
            pyglet.clock.schedule_once(lambda _: self.hide_sector(sector, immediate), 0.1)
            if G.world.get_active_dimension().get_chunk(*sector, generate=False).loaded:
                G.tickhandler.schedule_once(G.world.savefile.dump, None, "minecraft:chunk",
                                            dimension=self.active_dimension, chunk=sector)
        for sector in show:
            pyglet.clock.schedule_once(lambda _: self.show_sector(sector, immediate), 0.1)
            if not load_immediate:
                pyglet.clock.schedule_once(lambda _: G.world.savefile.read(
                    "minecraft:chunk", dimension=self.active_dimension, chunk=sector), 0.1)
            else:
                G.world.savefile.read("minecraft:chunk", dimension=self.active_dimension, chunk=sector)

        if not after: return
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if generate_chunks and abs(dx) <= config.CHUNK_GENERATION_RANGE and \
                        abs(dz) <= config.CHUNK_GENERATION_RANGE and self.config["enable_auto_gen"]:
                    chunk = self.get_active_dimension().get_chunk(dx+after[0], dz+after[1], generate=False)
                    if not chunk.generated:
                        G.worldgenerationhandler.add_chunk_to_generation_list(chunk, prior=True)

    def process_queue(self):
        if not any(type(x) == state.StatePartGame.StatePartGame for x in G.statehandler.active_state.parts):
            return
        start = time.time()
        while time.time() - start < 0.01:
            result = G.worldgenerationhandler.process_one_generation_task()
            if result is not None and not result: return

    def process_tasks(self, timer=0.2):
        """
        process an part of the array
        """
        dim: world.Dimension.Dimension = self.get_active_dimension()
        t = time.time()
        for chunk in list(dim.chunks.values()):
            for task in chunk.show_tasks:
                chunk._show_block(task, chunk.world[task])
                if time.time() - t > timer: return
            for task in chunk.hide_tasks:
                chunk._hide_block(task, chunk.world[task])
                if time.time() - t > timer: return
            while len(chunk.chunkgenerationtasks) > 0:
                task = chunk.chunkgenerationtasks.pop(0)
                task[0](*task[1], **task[2])
                if time.time() - t > timer: return
            for position in list(chunk.blockmap.keys()):
                args, kwargs, on_add = chunk.blockmap[position]
                blockinstance = chunk.add_block(*args, **kwargs)
                if on_add is not None:
                    on_add(blockinstance)
                if time.time() - t > timer: return
            chunk.show_tasks.clear()
            chunk.hide_tasks.clear()
            chunk.blockmap.clear()
            chunk.is_ready = True
            if time.time() - t > timer: return

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
                args, kwargs, on_add = chunk.blockmap[position]
                blockinstance = chunk.add_block(*args, **kwargs)
                if on_add is not None:
                    on_add(blockinstance)
            chunk.show_tasks.clear()
            chunk.hide_tasks.clear()
            chunk.blockmap.clear()
            chunk.is_ready = True

    def cleanup(self, remove_dims=False, filename=None):
        for dimension in self.dimensions.values():
            dimension: world.Dimension.Dimension
            for chunk in dimension.chunks.values():
                chunk.hide_all()
                chunk.world = {}
                chunk.is_ready = False
            dimension.chunks = {}
        if remove_dims:
            self.dimensions.clear()
        [inventory.on_world_cleared() for inventory in G.inventoryhandler.inventorys]
        self.reset_config()
        G.window.flying = False
        for inv in G.world.get_active_player().inventories.values(): inv.clear()
        self.spawnpoint = (random.randint(0, 15), random.randint(0, 15))
        G.worldgenerationhandler.tasks_to_generate.clear()
        G.worldgenerationhandler.runtimegenerationcache.clear()
        G.worldgenerationhandler.runtimegenerationcache = [[], {}, {}]
        self.players.clear()
        self.add_player("unknown")
        if filename is not None:
            self.setup_by_filename(filename)
        G.eventhandler.call("world:clean")

    def setup_by_filename(self, filename: str):
        self.filename = filename if filename is not None else "tmp"
        self.savefile = storage.SaveFile.SaveFile(self.filename)

