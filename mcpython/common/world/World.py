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
import random
import typing

import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.common.entity.PlayerEntity
import mcpython.common.state.GameViewStatePart
import mcpython.common.world.Chunk
import mcpython.common.world.Dimension
import mcpython.common.world.GameRule
import mcpython.common.world.OffProcessWorldAccess
import mcpython.common.world.SaveFile
import mcpython.engine.world.AbstractInterface
import mcpython.server.worldgen.WorldGenerationHandler
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.engine import logger


class World(mcpython.engine.world.AbstractInterface.IWorld):
    """
    Class holding all data of the world
    """

    def __init__(self, filename: str = None):
        shared.world = self

        # todo: add some more variation
        self.spawn_point: typing.Tuple[int, int] = (
            random.randint(0, 15),
            random.randint(0, 15),
        )

        # todo: change for str-based
        self.dimensions: typing.Dict[
            int, mcpython.engine.world.AbstractInterface.IDimension
        ] = {}

        self.dim_to_id: typing.Dict[str, int] = {}

        shared.dimension_handler.init_dims()

        # todo: change to str; todo: move to player; todo: make property
        self.active_dimension: int = 0

        # container for world-related config; contains: seed [build in] todo: move to config class
        self.config: typing.Dict[str, typing.Any] = {}

        # the gamerule handler fort his world
        self.gamerule_handler: typing.Union[
            mcpython.common.world.GameRule.GameRuleHandler, None
        ] = None

        self.reset_config()  # will reset the config

        # todo: move to configs / game rules
        self.hide_faces_to_not_generated_chunks: bool = True

        # the file-name to use, todo: make None if not needed
        self.filename: str = "tmp" if filename is None else filename

        # the save file instance
        self.save_file: mcpython.common.world.SaveFile.SaveFile = (
            mcpython.common.world.SaveFile.SaveFile(self.filename)
        )

        # when in an network, stores an reference to all other players
        self.players: typing.Dict[
            str, mcpython.common.entity.PlayerEntity.PlayerEntity
        ] = {}

        # The name of the local player; None on dedicated servers
        self.local_player: str = "unknown" if shared.IS_CLIENT else None

        self.world_loaded = False  # describes if the world is loaded or not

        self.world_generation_process = mcpython.common.world.OffProcessWorldAccess.OffProcessWorldHelper.spawn_process(
            self
        )

    def tick(self):
        for dimension in self.dimensions.values():
            if dimension.loaded:
                dimension.tick()

        self.world_generation_process.run_tasks()

    def add_player(
        self, name: str, add_inventories: bool = True, override: bool = True
    ):
        """
        Will add a new player into the world
        :param name: the name of the player to create
        :param add_inventories: if the inventories should be created
        :param override: if the player should be re-created if it exists in memory
        :return: the player instance
        """
        if name is None:
            raise ValueError("name cannot be None")

        if not override and name in self.players:
            return self.players[name]

        self.players[name] = shared.entity_manager.spawn_entity(
            "minecraft:player", (0, 0, 0), name
        )
        if add_inventories:
            self.players[name].create_inventories()
        return self.players[name]

    def get_active_player(
        self, create: bool = True
    ) -> typing.Union[mcpython.common.entity.PlayerEntity.PlayerEntity, None]:
        """
        Returns the player instance for this client
        :param create: if the player should be created or not (by calling add_player())
        :return: the player instance or None if no player with the name is arrival
        """
        if not create and self.local_player is None:
            return

        return (
            self.players[self.local_player]
            if self.local_player in self.players
            else self.add_player(self.local_player)
        )

    def get_player_by_name(self, name: str):
        if name not in self.players:
            self.add_player(name)

        return self.players[name]

    def player_iterator(self) -> typing.Iterable:
        return list(self.players.values())

    def entity_iterator(self) -> typing.Iterable:
        for dimension in self.dimensions.values():
            yield from dimension.entity_iterator()

    def reset_config(self):
        """
        Will reset the internal config of the system.
        todo: change game rule handler reset to an non-new-instance

        calls event world:reset_config in the process
        """
        self.config = {"enable_auto_gen": False, "enable_world_barrier": False}
        shared.event_handler.call("world:reset_config")
        self.gamerule_handler = mcpython.common.world.GameRule.GameRuleHandler(self)

    def get_active_dimension(
        self,
    ) -> typing.Union[mcpython.engine.world.AbstractInterface.IDimension, None]:
        """
        will return the dimension the player is in
        :return: the dimension or None if no dimension is set

        todo: move to player
        """
        return self.get_dimension(self.active_dimension)

    def get_dimension_names(self) -> typing.Iterable[str]:
        return self.dim_to_id.keys()

    def get_dimension_by_name(
        self, name: str
    ) -> mcpython.engine.world.AbstractInterface.IDimension:
        return self.dimensions[self.dim_to_id[name]]

    def add_dimension(
        self, dim_id: int, name: str, dim_config=None
    ) -> mcpython.engine.world.AbstractInterface.IDimension:
        """
        will add an new dimension into the system
        :param dim_id: the id to create under
        :param name: the name of the dimension
        :param dim_config: the dim_config to use as gen config
        :return: the dimension instance
        """
        if dim_config is None:
            dim_config = {}
        dim = self.dimensions[dim_id] = mcpython.common.world.Dimension.Dimension(
            self, dim_id, name, gen_config=dim_config
        )
        self.dim_to_id[dim.name] = dim_id
        shared.world_generation_handler.setup_dimension(dim, dim_config)
        return dim

    def join_dimension(self, dim_id: int):
        """
        will change the dimension of the active player
        :param dim_id: the dimension to change to todo: make str
        todo: move to player
        """
        logger.println("changing dimension to '{}'...".format(dim_id))

        shared.event_handler.call("dimension:change:pre", self.active_dimension, dim_id)

        sector = mcpython.util.math.position_to_chunk(
            shared.world.get_active_player().position
        )
        logger.println("unloading chunks...")
        self.change_chunks(sector, None)
        old = self.active_dimension
        self.active_dimension = dim_id
        logger.println("loading new chunks...")
        self.change_chunks(None, sector)
        shared.event_handler.call("dimension:chane:post", old, dim_id)
        logger.println("finished!")

    def get_dimension(
        self, dim_id: int
    ) -> mcpython.engine.world.AbstractInterface.IDimension:
        """
        will get an dimension with an special id
        :param dim_id: the id to use
        :return: the dimension instance or None if it does not exist
        """
        if dim_id in self.dimensions:
            return self.dimensions[dim_id]

        if dim_id in self.dim_to_id:
            return self.dimensions[self.dim_to_id[dim_id]]

        # logger.print_stack("[ERROR] failed to access dim '{}', below call stack".format(dim_id))

    def hit_test(
        self,
        position: typing.Tuple[float, float, float],
        vector: typing.Tuple[float, float, float],
        max_distance: int = 8,
    ) -> typing.Union[
        typing.Tuple[
            typing.Tuple[int, int, int],
            typing.Tuple[int, int, int],
            typing.Tuple[float, float, float],
        ],
        typing.Tuple[None, None, None],
    ]:
        """
        Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None, None

        Will check for bounding boxes of blocks

        :param position: The (x, y, z) position to check visibility from
        :param vector: The line of sight vector
        :param max_distance: How many blocks away to search for a hit

        todo: cache the bbox of the block
        todo: move to dimension
        todo: add variant only taking the player
        todo: cache when possible
        todo: add variant for entities
        """
        m = shared.world.gamerule_handler.table[
            "hitTestSteps"
        ].status.status  # get m from the gamerule
        x, y, z = position
        dx, dy, dz = vector
        dx /= m
        dy /= m
        dz /= m
        previous = None
        for _ in range(max_distance * m):
            key = mcpython.util.math.normalize((x, y, z))
            block = self.get_active_dimension().get_block(key)
            if (
                block
                and type(block) != str
                and block.get_view_bbox().test_point_hit((x, y, z), block.position)
            ):
                return key, previous, (x, y, z)
            if key != previous:
                previous = key
            x += dx
            y += dy
            z += dz
        return None, None, None

    def show_chunk(
        self,
        chunk: typing.Union[
            typing.Tuple[int, int], mcpython.engine.world.AbstractInterface.IChunk
        ],
    ):
        """
        Ensure all blocks in the given chunk that should be shown are
        drawn to the canvas.
        :param chunk: the chunk to show
        """
        if not issubclass(type(chunk), mcpython.engine.world.AbstractInterface.IChunk):
            chunk = self.get_active_dimension().get_chunk(*chunk, generate=False)
        if chunk is None:
            return
        chunk.show()

    def hide_chunk(
        self,
        chunk: typing.Union[
            typing.Tuple[int, int], mcpython.engine.world.AbstractInterface.IChunk
        ],
    ):
        """
        Ensure all blocks in the given chunk that should be hidden are
        removed from the canvas.
        :param chunk: the chunk to hide
        """
        if not issubclass(type(chunk), mcpython.engine.world.AbstractInterface.IChunk):
            chunk = self.get_active_dimension().get_chunk(*chunk, generate=False)
        if chunk is None:
            return
        chunk.hide()

    def change_chunks(
        self,
        before: typing.Union[typing.Tuple[int, int], None],
        after: typing.Union[typing.Tuple[int, int], None],
        generate_chunks=True,
        load_immediate=True,
    ):
        """
        Move from chunk `before` to chunk `after`
        :param before: the chunk before
        :param after: the chunk after
        :param generate_chunks: if chunks should be generated
        :param load_immediate: if chunks should be loaded immediate if needed
        todo: move to dimension
        """
        if self.get_active_dimension() is None:
            return

        before_set = set()
        after_set = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if before is not None:
                    x, z = before
                    if (dx + x) ** 2 + (dz + z) ** 2 <= (pad + 1) ** 2:
                        before_set.add((x + dx, z + dz))
                if after is not None:
                    x, z = after
                    if (dx + x) ** 2 + (dz + z) ** 2 <= (pad + 1) ** 2:
                        after_set.add((x + dx, z + dz))
        # show = after_set - before_set
        hide = before_set - after_set
        for chunk in hide:
            # todo: fix this, this was previously hiding chunks randomly....
            pyglet.clock.schedule_once(lambda _: self.hide_chunk(chunk), 0.1)
            c = shared.world.get_active_dimension().get_chunk(*chunk, generate=False, create=False)

            if c and c.loaded and not shared.IS_NETWORKING:
                shared.tick_handler.schedule_once(
                    shared.world.save_file.dump,
                    None,
                    "minecraft:chunk",
                    dimension=self.active_dimension,
                    chunk=chunk,
                )

        for chunk in after_set:
            c = self.get_active_dimension().get_chunk(*chunk, generate=False, create=False)
            if c and c.is_visible():
                continue

            pyglet.clock.schedule_once(lambda _: self.show_chunk(chunk), 0.1)

            if not shared.IS_NETWORKING:
                if not load_immediate:
                    pyglet.clock.schedule_once(
                        lambda _: shared.world.save_file.read(
                            "minecraft:chunk", dimension=self.active_dimension, chunk=chunk
                        ),
                        0.1,
                    )
                else:
                    shared.world.save_file.read(
                        "minecraft:chunk", dimension=self.active_dimension, chunk=chunk
                    )
            else:
                self.get_active_dimension().get_chunk(*chunk, generate=False)

        if not after or shared.IS_NETWORKING:
            return

        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                if (
                    generate_chunks
                    and abs(dx) <= mcpython.common.config.CHUNK_GENERATION_RANGE
                    and abs(dz) <= mcpython.common.config.CHUNK_GENERATION_RANGE
                    and self.config["enable_auto_gen"]
                ):
                    chunk = self.get_active_dimension().get_chunk(
                        dx + after[0], dz + after[1], generate=False
                    )
                    if not chunk.is_generated():
                        shared.world_generation_handler.add_chunk_to_generation_list(
                            chunk
                        )

    def cleanup(self, remove_dims=False, filename=None):
        """
        will clean up the world
        :param remove_dims: if dimensions should be cleared
        :param filename: the new filename if it changes
        todo: make split up into smaller functions
        """
        self.active_dimension = 0
        for dimension in self.dimensions.values():
            dimension: mcpython.engine.world.AbstractInterface.IDimension
            for chunk in dimension.chunks.values():
                chunk.hide_all()
                del chunk
            dimension.chunks = {}
        if remove_dims:
            self.dimensions.clear()
            shared.dimension_handler.init_dims()
        [
            inventory.on_world_cleared()
            for inventory in shared.inventory_handler.containers
        ]
        self.reset_config()

        if shared.IS_CLIENT:
            shared.world.get_active_player().flying = False
            for inv in shared.world.get_active_player().get_inventories():
                inv.clear()

        self.spawn_point = (random.randint(0, 15), random.randint(0, 15))
        shared.world_generation_handler.task_handler.clear()
        shared.entity_manager.clear()
        self.players.clear()
        if filename is not None:
            self.setup_by_filename(filename)
        mcpython.common.data.DataPacks.datapack_handler.cleanup()
        shared.event_handler.call("world:clean")

    def setup_by_filename(self, filename: str):
        """
        will set up the system for an new file name
        :param filename: the file name to use
        """
        self.filename = filename if filename is not None else "tmp"
        self.save_file = mcpython.common.world.SaveFile.SaveFile(self.filename)
