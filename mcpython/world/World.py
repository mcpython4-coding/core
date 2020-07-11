"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import random
import typing

import deprecation
import pyglet

import globals as G
import mcpython.chat.DataPack
import mcpython.config
import mcpython.state.StatePartGame
import mcpython.storage.SaveFile
import mcpython.util.math
import mcpython.world.Chunk
import mcpython.world.Dimension
import mcpython.world.GameRule
import mcpython.world.gen.WorldGenerationHandler
import mcpython.world.player
import logger


class World:
    """
    class holding all data of the world
    """

    def __init__(self, filename: str = None):
        G.world = self
        # todo: add some more variation
        self.spawnpoint: typing.Tuple[int, int] = (random.randint(0, 15), random.randint(0, 15))
        self.dimensions: typing.Dict[int, mcpython.world.Dimension.Dimension] = {}  # todo: change for str-based
        G.dimensionhandler.init_dims()
        self.active_dimension: int = 0  # todo: change to str; todo: move to player; todo: make property
        # container for world-related config; contains: seed [build in] todo: move to config class
        self.config: typing.Dict[str, typing.Any] = {}
        self.gamerulehandler: typing.Union[
            mcpython.world.GameRule.GameRuleHandler, None] = None  # the gamerule handler fort his world
        self.reset_config()  # will reset the config
        self.CANCEL_DIM_CHANGE: bool = False  # flag for canceling the dim change event
        self.hide_faces_to_ungenerated_chunks: bool = True  # todo: move to configs
        self.filename: str = "tmp" if filename is None else filename  # the file-name to use, todo: make None if not needed
        self.savefile: mcpython.storage.SaveFile.SaveFile = mcpython.storage.SaveFile.SaveFile(
            self.filename)  # the save file instance

        # when in an network, stores an reference to all other players
        self.players: typing.Dict[str, mcpython.world.player.Player] = {}
        # self.add_player("unknown", add_inventories=False)
        self.active_player: str = "unknown"  # todo: make property, make None-able & set default None when not in world
        self.world_loaded = False  # describes if the world is loaded or not

    def add_player(self, name: str, add_inventories: bool = True, override: bool = True):
        """
        will add an new player into the world
        :param name: the name of the player to create
        :param add_inventories: if the inventories should be created
        :param override: if the player should be re-created if it exists in memory
        :return: the player instance
        """
        if not override and name in self.players: return self.players[name]
        self.players[name] = G.entityhandler.add_entity("minecraft:player", (0, 0, 0), name)
        if add_inventories:
            self.players[name].create_inventories()
        return self.players[name]

    def get_active_player(self, create: bool = True) -> typing.Union[mcpython.world.player.Player, None]:
        """
        returns the player instance for this client
        :param create: if the player should be created or not
        :return: the player instance or None if no player is set
        """
        if not create and self.active_player is None: return
        return self.players[self.active_player] if self.active_player in self.players else self.add_player(
            self.active_player)

    def reset_config(self):
        """
        Will reset the internal config of the system.
        todo: change game rule handler reset to an non-new-instance

        calls event world:reset_config in the process
        """
        self.config = {"enable_auto_gen": False, "enable_world_barrier": False}
        G.eventhandler.call("world:reset_config")
        self.gamerulehandler = mcpython.world.GameRule.GameRuleHandler(self)

    def get_active_dimension(self) -> typing.Union[mcpython.world.Dimension.Dimension, None]:
        """
        will return the dimension the player is in
        :return: the dimension or None if no dimension is set

        todo: move to player
        """
        return self.get_dimension(self.active_dimension)

    def add_dimension(self, dim_id: int, name: str, dim_config=None, config=None) -> mcpython.world.Dimension.Dimension:
        """
        will add an new dimension into the system
        :param dim_id: the id to create under
        :param name: the name of the dimension
        :param config: deprecated, replaced by dim_config
        :param dim_config: the dim_config to use as gen config
        :return: the dimension instance
        """
        if dim_config is None: dim_config = config
        if dim_config is None: dim_config = {}
        dim = self.dimensions[dim_id] = mcpython.world.Dimension.Dimension(self, dim_id, name, genconfig=dim_config)
        G.worldgenerationhandler.setup_dimension(dim, config)
        return dim

    def join_dimension(self, dim_id: int, save_current=None):
        """
        will change the dimension of the active player
        :param dim_id: the dimension to change to todo: make str
        :param save_current: unused, deprecated; always set to True now
        todo: move to player
        """
        logger.println("changing dimension to '{}'...".format(dim_id))
        self.CANCEL_DIM_CHANGE = False
        G.eventhandler.call("dimension:chane:pre", self.active_dimension, dim_id)
        if self.CANCEL_DIM_CHANGE:
            logger.println("interrupted!")
            return
        sector = mcpython.util.math.positionToChunk(G.world.get_active_player().position)
        logger.println("unloading chunks...")
        self.change_chunks(sector, None)
        old = self.active_dimension
        self.active_dimension = dim_id
        logger.println("loading new chunks...")
        self.change_chunks(None, sector)
        G.eventhandler.call("dimension:chane:post", old, dim_id)
        logger.println("finished!")

    def get_dimension(self, dim_id: int) -> mcpython.world.Dimension.Dimension:
        """
        will get an dimension with an special id
        :param dim_id: the id to use
        :return: the dimension instance or None if it does not exist
        """
        if dim_id in self.dimensions: return self.dimensions[dim_id]

    def hit_test(self, position: typing.Tuple[float, float, float], vector: typing.Tuple[float, float, float],
                 max_distance: int = 8) -> typing.Union[
            typing.Tuple[typing.Tuple[int, int, int], typing.Tuple[int, int, int], typing.Tuple[float, float, float]],
            typing.Tuple[None, None, None]]:
        """
        Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None, None

        Will check for bounding boxes of blocks

        :param position: The (x, y, z) position to check visibility from
        :param vector: The line of sight vector
        :param max_distance: How many blocks away to search for a hit

        todo: cache the bbox of the block
        """
        m = G.world.gamerulehandler.table["hitTestSteps"].status.status  # get m from the gamerule
        x, y, z = position
        dx, dy, dz = vector
        dx /= m
        dy /= m
        dz /= m
        previous = None
        for _ in range(max_distance * m):
            key = mcpython.util.math.normalize((x, y, z))
            blocki = self.get_active_dimension().get_block(key)
            if blocki and type(blocki) != str and blocki.get_view_bbox().test_point_hit((x, y, z), blocki.position):
                return key, previous, (x, y, z)
            if key != previous:
                previous = key
            x += dx
            y += dy
            z += dz
        return None, None, None

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def show_sector(self, sector): self.show_chunk(sector)

    def show_chunk(self, chunk: typing.Union[typing.Tuple[int, int], mcpython.world.Chunk.Chunk]):
        """
        Ensure all blocks in the given chunk that should be shown are
        drawn to the canvas.
        :param chunk: the chunk to show
        """
        if not issubclass(type(chunk), mcpython.world.Chunk.Chunk):
            chunk = self.get_active_dimension().get_chunk(*chunk, generate=False)
        chunk.show()

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def hide_sector(self, sector, immediate=False): self.hide_chunk(sector)

    def hide_chunk(self, chunk: typing.Union[typing.Tuple[int, int], mcpython.world.Chunk.Chunk]):
        """
        Ensure all blocks in the given chunk that should be hidden are
        removed from the canvas.
        :param chunk: the chunk to hide
        """
        if not issubclass(type(chunk), mcpython.world.Chunk.Chunk):
            chunk = self.get_active_dimension().get_chunk(*chunk, generate=False)
        chunk.hide()

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def change_sectors(self, before, after, immediate=False, generate_chunks=True, load_immediate=False):
        self.change_chunks(before, after, generate_chunks, load_immediate)

    def change_chunks(self, before: typing.Union[typing.Tuple[int, int], None], after: typing.Union[typing.Tuple[int, int], None], generate_chunks=True,
                      load_immediate=True):
        """
        Move from chunk `before` to chunk `after`
        :param before: the chunk before
        :param after: the chunk after
        :param generate_chunks: if chunks should be generated
        :param load_immediate: if chunks should be loaded immediate if needed
        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if dx ** 2 + dz ** 2 > (pad + 1) ** 2:
                    continue
                if before:
                    x, z = before
                    before_set.add((x + dx, z + dz))
                if after:
                    x, z = after
                    after_set.add((x + dx, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for chunk in hide:
            pyglet.clock.schedule_once(lambda _: self.hide_chunk(chunk), 0.1)
            if G.world.get_active_dimension().get_chunk(*chunk, generate=False).loaded:
                G.tickhandler.schedule_once(G.world.savefile.dump, None, "minecraft:chunk",
                                            dimension=self.active_dimension, chunk=chunk)
        for chunk in show:
            pyglet.clock.schedule_once(lambda _: self.show_chunk(chunk), 0.1)
            if not load_immediate:
                pyglet.clock.schedule_once(lambda _: G.world.savefile.read(
                    "minecraft:chunk", dimension=self.active_dimension, chunk=chunk), 0.1)
            else:
                G.world.savefile.read("minecraft:chunk", dimension=self.active_dimension, chunk=chunk)

        if not after: return
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if generate_chunks and abs(dx) <= mcpython.config.CHUNK_GENERATION_RANGE and \
                        abs(dz) <= mcpython.config.CHUNK_GENERATION_RANGE and self.config["enable_auto_gen"]:
                    chunk = self.get_active_dimension().get_chunk(dx + after[0], dz + after[1], generate=False)
                    if not chunk.generated:
                        G.worldgenerationhandler.add_chunk_to_generation_list(chunk, prior=True)

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def process_queue(self):
        if not any(type(x) == mcpython.state.StatePartGame.StatePartGame for x in G.statehandler.active_state.parts):
            return
        G.worldgenerationhandler.task_handler.process_tasks(timer=0.02)

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def process_tasks(self, timer=0.2):
        G.worldgenerationhandler.task_handler.process_tasks(timer=timer)

    @deprecation.deprecated("dev1-4", "a1.3.0")
    def process_entire_queue(self):
        G.worldgenerationhandler.task_handler.process_tasks()

    def cleanup(self, remove_dims=False, filename=None, add_player=False):
        """
        will clean up the world
        :param remove_dims: if dimensions should be cleared
        :param filename: the new filename if it changes
        :param add_player: if the player should be added
        todo: make split up into smaller functions
        """
        for dimension in self.dimensions.values():
            dimension: mcpython.world.Dimension.Dimension
            for chunk in dimension.chunks.values():
                chunk.hide_all()
                del chunk
            dimension.chunks = {}
        if remove_dims:
            self.dimensions.clear()
            G.dimensionhandler.init_dims()
        [inventory.on_world_cleared() for inventory in G.inventoryhandler.inventorys]
        self.reset_config()
        G.world.get_active_player().flying = False
        for inv in G.world.get_active_player().inventories.values(): inv.clear()
        self.spawnpoint = (random.randint(0, 15), random.randint(0, 15))
        G.worldgenerationhandler.task_handler.clear()
        self.players.clear()
        if add_player: self.add_player("unknown")
        if filename is not None:
            self.setup_by_filename(filename)
        mcpython.chat.DataPack.datapackhandler.cleanup()
        G.eventhandler.call("world:clean")

    def setup_by_filename(self, filename: str):
        """
        will set up the system for an new file name
        :param filename: the file name to use
        """
        self.filename = filename if filename is not None else "tmp"
        self.savefile = mcpython.storage.SaveFile.SaveFile(self.filename)
