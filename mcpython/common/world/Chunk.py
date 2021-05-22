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
import datetime
import typing

import mcpython.common.block.AbstractBlock as Block
import mcpython.common.world.AbstractInterface
import mcpython.server.worldgen.map.AbstractChunkInfoMap
import mcpython.util.enums
import mcpython.util.math
from mcpython import logger, shared


class Chunk(mcpython.common.world.AbstractInterface.IChunk):
    """
    representation of an chunk in the world
    """

    BLOCK_REGISTRY = shared.registry.get_by_name("minecraft:block")

    now = datetime.datetime.now()  # when is now?

    def __init__(
        self,
        dimension: mcpython.common.world.AbstractInterface.IDimension,
        position: typing.Tuple[int, int],
    ):
        """
        Will create a new chunk instance
        :param dimension: the world.Dimension.Dimension object used to store this chunk
        :param position: the position of the chunk
        WARNING: use Dimension.get_chunk() where possible [saver variant, will do some work in the background]
        """
        super().__init__()
        self.dimension = dimension

        # The position of the chunk
        self.position = tuple(int(e) for e in position)

        # Used when the chunks gets invalid or is loaded at the moment
        self.is_ready = False

        # Indicated that the chunk is shown to the player
        # todo: client-only
        self.visible = False

        # Indicated that the chunk is loaded
        self.loaded = False

        # Indicates that the chunk is generated
        self.generated = False

        # Indicated that the chunk was modified
        self.dirty = False

        # Creates the needed chunk maps as defined in the world generation handler
        shared.world_generation_handler.setup_chunk_maps(self)

        # For all default chunks, we add such ticket. todo: remove & set only when needed
        self.add_chunk_load_ticket(
            mcpython.common.world.AbstractInterface.ChunkLoadTicketType.SPAWN_CHUNKS
        )

    def entity_iterator(self) -> typing.Iterable:
        return tuple(self.entities)

    def tick(self):
        """
        General chunk tick
        todo: move random ticks & entity ticks here
        """

        self.check_for_unload()

    def save(self):
        shared.world.save_file.dump(
            self, "minecraft:chunk", dimension=self.get_dimension(), chunk=self.position
        )

    def as_shareable(self) -> mcpython.common.world.AbstractInterface.IChunk:
        return self

    def mark_dirty(self):
        self.dirty = True
        return self

    def get_dimension(self) -> mcpython.common.world.AbstractInterface.IDimension:
        return self.dimension

    def get_position(self) -> typing.Tuple[int, int]:
        return self.position

    def get_maximum_y_coordinate_from_generation(
        self, x: int, z: int, default=None
    ) -> int:
        """
        Helper function for getting the y height at the given xz generation based on the generation code, by looking
            up the internal map
        :param x: the x coord
        :param z: the y coord
        :param default: the default value when no value is set
        :return: the y value at that position
        """
        height_map = self.get_map("minecraft:height_map")
        return height_map.get_at_xz(x, z)[0][1] if (x, z) in height_map else default

    def draw(self):
        """
        Will draw the chunk with the content for it
        Draws all entities
        todo: for this, add a batch

        Will schedule a chunk load from saves when needed
        """
        if not self.is_ready or not self.visible:
            return

        # todo: add a list of blocks which want an draw() call

        # load if needed
        if not self.loaded:
            shared.tick_handler.schedule_once(
                shared.world.save_file.read,
                "minecraft:chunk",
                dimension=self.dimension.get_id(),
                chunk=self.position,
            )

        # todo: can we also use batches & manipulate vertex data?
        #  [WIP, see rendering/entities/EntityBoxRenderingHelper.py]
        for entity in self.entities:
            entity.draw()

    ALL_FACES_EXPOSED = {x: True for x in mcpython.util.enums.EnumSide.iterate()}

    def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[str, bool]:
        """
        Returns an dict of the exposed status of every face of the given block
        :param position: the position to check
        :return: the dict for the status
        """
        instance = self.get_block(position)

        if instance is None or type(instance) == str:
            return self.ALL_FACES_EXPOSED.copy()

        faces = {}

        for face in mcpython.util.enums.FACE_ORDER:
            pos = face.relative_offset(position)
            chunk_position = mcpython.util.math.position_to_chunk(pos)

            if chunk_position != self.position:
                chunk = self.dimension.get_chunk(chunk_position, generate=False)

                if chunk is None:
                    continue
            else:
                chunk = self

            if (
                not chunk.is_loaded()
                and shared.world.hide_faces_to_not_generated_chunks
            ):
                faces[face.normal_name] = False
            else:
                block = chunk.get_block(pos)

                faces[face.normal_name] = block is None or (
                    not isinstance(block, str)
                    and (
                        not block.face_solid[face.invert()]
                        or not instance.face_solid[face]
                    )
                )

        return faces

    def exposed_faces_iterator(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Iterator[mcpython.util.enums.EnumSide]:
        instance = self.get_block(position)

        if instance is None or type(instance) == str:
            yield from mcpython.util.enums.EnumSide.iterate()

        for face in mcpython.util.enums.FACE_ORDER:
            pos = face.relative_offset(position)
            chunk_position = mcpython.util.math.position_to_chunk(pos)

            if chunk_position != self.position:
                chunk = self.dimension.get_chunk(chunk_position, generate=False)

                if chunk is None:
                    continue
            else:
                chunk = self

            if not (
                not chunk.is_loaded()
                and shared.world.hide_faces_to_not_generated_chunks
            ):
                block = chunk.get_block(pos)

                if not (
                    block is None
                    or (
                        not isinstance(block, str)
                        and (
                            not block.face_solid[face.invert()]
                            or not instance.face_solid[face]
                        )
                    )
                ):
                    yield face

    def is_position_blocked(self, position: typing.Tuple[float, float, float]) -> bool:
        """
        Will return if at a given position is a block or a block is scheduled [e.g. by world generation]
        :param position: the position to check
        :return: if there is an block
        """
        return (
            position in self._world
            or shared.world_generation_handler.task_handler.get_block(position, self)
            is not None
        )

    def add_block(
        self,
        position: tuple,
        block_name: typing.Union[str, Block.AbstractBlock],
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable[[Block.AbstractBlock], None] = None,
        check_build_range=True,
        block_state=None,
        replace_existing=True,
    ):
        """
        Adds a block to the given position
        :param position: the position to add
        :param block_name: the name of the block or an instance of it
        :param immediate: if the block should be shown if needed
        :param block_update: if an block-update should be send to neighbors blocks
        :param block_update_self: if the block should get an block-update
        :param lazy_setup: an callable for setting up the block instance
        :param check_build_range: if the build limits should be checked
        :param block_state: the block state to create in, or None if not set
        :param replace_existing: if existing blocks should be replaced
        :return: the block instance or None if it could not be created
        """
        # check if it is in build range
        r = self.dimension.get_dimension_range()
        if check_build_range and (position[1] < r[0] or position[1] > r[1]):
            return

        if position != mcpython.util.math.normalize(position):
            raise ValueError(
                "position '{}' is no valid block position".format(position)
            )

        if position in self._world:
            if not replace_existing:
                return

            self.remove_block(
                position,
                immediate=immediate,
                block_update=block_update,
                block_update_self=block_update_self,
            )

        if block_name in [None, "air", "minecraft:air"]:
            return

        if issubclass(type(block_name), Block.AbstractBlock):
            block = block_name
            block.position = position
            block.dimension = self.dimension.get_name()

            if lazy_setup is not None:
                lazy_setup(block)

            if shared.IS_CLIENT:
                block.face_state.update()

        # Create the block instance from the registry
        else:
            if not self.BLOCK_REGISTRY.is_valid_key(block_name):
                return

            block_cls = self.BLOCK_REGISTRY.get(block_name)

            block = block_cls()
            block.position = position
            block.dimension = self.dimension.get_name()
            if lazy_setup is not None:
                lazy_setup(block)

        # store the block instance in the local world
        self._world[position] = block

        block.on_block_added()

        if block_state is not None:
            block.set_model_state(block_state)

        self.mark_dirty()
        self.mark_position_dirty(position)

        if immediate and shared.IS_CLIENT:
            block.face_state.update()

            if block_update:
                self.on_block_updated(position, include_itself=block_update_self)

            self.check_neighbors(position)

        return block

    def on_block_updated(
        self, position: typing.Tuple[int, int, int], include_itself=True
    ):
        """
        Will call to the neighbor blocks an block update
        :param position: the position in the center
        :param include_itself: if the block itself should be updated
        """
        x, y, z = position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if [dx, dy, dz].count(0) >= 2 and not (
                        not include_itself and dx == dy == dz == 0
                    ):
                        b: Block.AbstractBlock = self.dimension.get_block(
                            (x + dx, y + dy, z + dz)
                        )
                        if b and type(b) != str:
                            try:
                                b.on_block_update()
                            except:
                                logger.print_exception(
                                    "during block-updating block {} caused by block at {}".format(
                                        b, position
                                    )
                                )

    def remove_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=Block.BlockRemovalReason.UNKNOWN,
    ):
        """
        Remove the block at the given `position`.
        :param position: The (x, y, z) position of the block to remove.
        :param immediate: Whether or not to immediately remove block from canvas.
        :param block_update: Whether an block-update should be called or not
        :param block_update_self: Whether the block to remove should get an block-update or not
        :param reason: the reason why the block was removed
        """
        if position not in self._world:
            return

        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        self._world[position].on_block_remove(reason)

        if shared.IS_CLIENT:
            self._world[position].face_state.hide_all()

        del self._world[position]

        if block_update:
            self.on_block_updated(position, include_itself=block_update_self)

        if immediate:
            self.check_neighbors(position)

        self.mark_position_dirty(position)
        self.mark_dirty()

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        """
        Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
        :param position: the position as the center
        """
        # Only do this on the client
        if not shared.IS_CLIENT:
            return

        # for each block touching, do...
        for face in mcpython.util.enums.EnumSide.iterate():
            block = self.dimension.get_block(
                face.relative_offset(position), none_if_str=True
            )
            if block is None:
                continue

            block.face_state.update(True)

    def show_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
    ):
        """
        Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
        :param position: The (x, y, z) position of the block to show.
        :param immediate: Whether or not to show the block immediately.
        """
        if not shared.IS_CLIENT:
            return

        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        if position not in self._world:
            return

        if immediate:
            self._world[position].face_state.update(redraw_complete=True)
        else:
            shared.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

        self.mark_dirty()

    def hide_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate=True,
    ):
        """
        Hide the block at the given `position`. Hiding does not remove the
        block from the world.
        :param position: The (x, y, z) position of the block to hide.
        :param immediate: Whether or not to immediately remove the block from the canvas.
        """
        if not shared.IS_CLIENT:
            return

        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        if immediate:
            if position not in self._world:
                return
            self._world[position].face_state.hide_all()
        else:
            shared.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

        self.mark_dirty()

    def show(self, force=False):
        """
        will show the chunk
        :param force: if the chunk show should be forced or not
        """
        if not shared.IS_CLIENT:
            return

        if self.visible and not force:
            return

        self.visible = True
        self.update_visible()
        self.mark_dirty()

    def hide(self, force=False):
        """
        will hide the chunk
        :param force: if the chunk hide should be forced or not
        """
        if not shared.IS_CLIENT:
            return

        if not self.visible and not force:
            return

        self.visible = False
        self.hide_all()
        self.mark_dirty()

    def is_visible(self) -> bool:
        return self.visible and shared.IS_CLIENT

    def update_visible_block(self, position: typing.Tuple[int, int, int], hide=True):
        if not shared.IS_CLIENT:
            return

        self.mark_position_dirty(position)

        if not self.exposed(position):
            self.hide_block(position)
        elif hide:
            self.show_block(position)

    def exposed(self, position: typing.Tuple[int, int, int]) -> bool:
        return any(self.exposed_faces(position).values())

    def update_visible(self, hide=True, immediate=False):
        """
        will update all visible of all blocks of the chunk
        :param hide: if blocks should be hidden if needed
        :param immediate: if immediate call or not
        """
        if not shared.IS_CLIENT:
            return

        for position in self._world.keys():
            if immediate:
                shared.world_generation_handler.task_handler.schedule_visual_update(
                    self, position
                )
            else:
                self.update_visible_block(position, hide=hide)

    def hide_all(self, immediate=True):
        """
        will hide all blocks in the chunk
        :param immediate: if immediate or not
        """
        if not shared.IS_CLIENT:
            return

        for position in self._world:
            self.hide_block(position, immediate=immediate)

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[Block.AbstractBlock, str, None]:
        """
        will get the block at an given position
        :param position: the position to check for, must be normalized
        :param none_if_str: if none if the block instance is str
        :return: None if no block, str if scheduled and Block.Block if created
        todo: split up into get_block_generated and get_block_un_generated
        """
        return (
            self._world[position]
            if position in self._world
            else (
                shared.world_generation_handler.task_handler.get_block(
                    position, chunk=self
                )
                if not none_if_str
                else None
            )
        )

    def __str__(self):
        return "Chunk(dimension={},position={})".format(
            self.dimension.get_id(), self.position
        )

    def is_loaded(self) -> bool:
        return self.loaded

    def is_generated(self) -> bool:
        return self.generated

    def get_entities(self):
        return self.entities

    def dump_debug_maps(self, file_formatter: str):
        for m in self.data_maps.values():
            m.dump_debug_info(file_formatter.format(m.NAME.replace(":", "_")))
