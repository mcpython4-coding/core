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
import asyncio
import datetime
import typing

import deprecation
import mcpython.common.block.AbstractBlock as Block
import mcpython.engine.world.AbstractInterface
import mcpython.server.worldgen.map.AbstractChunkInfoMap
import mcpython.util.math
from bytecodemanipulation.OptimiserAnnotations import (
    builtins_are_static,
    constant_operation,
    forced_attribute_type,
    name_is_static,
    object_method_is_protected,
    returns_argument,
)
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.common.entity.ItemEntity import ItemEntity
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.enums import EnumSide
from mcpython.util.math import normalize, position_to_chunk


@forced_attribute_type("position", lambda: tuple)
@forced_attribute_type("is_ready", lambda: bool)
@forced_attribute_type("visible", lambda: bool)
@forced_attribute_type("loaded", lambda: bool)
@forced_attribute_type("generated", lambda: bool)
@forced_attribute_type("dirty", lambda: bool)
class Chunk(mcpython.engine.world.AbstractInterface.IChunk):
    """
    Default representation of a chunk in the world

    Defines the default behaviour
    """

    BLOCK_REGISTRY = shared.registry.get_by_name("minecraft:block")

    now = datetime.datetime.now()  # when is now?

    @builtins_are_static()
    def __init__(
        self,
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
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

        if shared.world_generation_handler is not None:
            # Creates the needed chunk maps as defined in the world generation handler
            shared.world_generation_handler.setup_chunk_maps(self)

        # For all default chunks, we add such ticket. todo: remove & set only when needed
        self.add_chunk_load_ticket(
            mcpython.engine.world.AbstractInterface.ChunkLoadTicketType.SPAWN_CHUNKS
        )

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        from mcpython.common.world.serializer.Chunk import Chunk as ChunkSerializer

        await ChunkSerializer.save_to_buffer(buffer, self)

    async def read_from_network_buffer(self, buffer: ReadBuffer, immediate=False):
        from mcpython.common.world.serializer.Chunk import Chunk as ChunkSerializer

        await ChunkSerializer.read_from_buffer(buffer, self, immediate=immediate)

    @builtins_are_static()
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

    @returns_argument()
    def mark_dirty(self):
        self.dirty = True
        return self

    @constant_operation()
    def get_dimension(self) -> mcpython.engine.world.AbstractInterface.IDimension:
        return self.dimension

    @constant_operation()
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
        :return: the y value at that position, maybe negative
        """
        height_map = self.get_map("minecraft:height_map")
        return height_map.get_at_xz(x, z)[0][1] if (x, z) in height_map else default

    @builtins_are_static()
    @name_is_static("shared", lambda: shared)
    def draw(self):
        """
        Will draw the chunk with the content for it
        Draws all entities
        todo: for this, add a batch

        Will schedule a chunk load from saves when needed
        """
        # todo: can we cache this somehow?
        if not self.is_ready or not self.visible:
            return

        # todo: add a list of blocks which want an draw() call

        # load if needed
        if not self.loaded:
            shared.tick_handler.schedule_once(
                shared.world.save_file.read,
                "minecraft:chunk",
                dimension=self.dimension.get_dimension_id(),
                chunk=self.position,
            )

        # todo: can we also use batches & manipulate vertex data?
        #  [WIP, see rendering/entities/EntityBoxRenderingHelper.py]
        for entity in self.entities:
            entity.draw()

    ALL_FACES_EXPOSED = {x: True for x in EnumSide.iterate()}

    @deprecation.deprecated()
    @builtins_are_static()
    @name_is_static("EnumSide", lambda: EnumSide)
    @name_is_static("position_to_chunk", lambda: position_to_chunk)
    def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[str, bool]:
        """
        Returns a dict of the exposed status of every face of the given block

        :param position: the position to check
        :return: the dict for the status
        """
        instance = self.get_block(position, none_if_str=True)

        if instance is None:
            return self.ALL_FACES_EXPOSED.copy()

        faces = {}

        for face in EnumSide.iterate():
            pos = face.relative_offset(position)
            chunk_position = position_to_chunk(pos)

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
                        not block.face_solid & face.invert().bitflag
                        or not instance.face_solid & face.bitflag
                    )
                )

        return faces

    @deprecation.deprecated()
    @builtins_are_static()
    @name_is_static("EnumSide", lambda: EnumSide)
    @name_is_static("position_to_chunk", lambda: position_to_chunk)
    def exposed_faces_list(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.List[bool]:
        instance = self.get_block(position, none_if_str=True)

        if instance is None:
            return [True] * 6

        faces = [False] * 6

        for face in EnumSide.iterate():
            pos = face.relative_offset(position)
            chunk_position = position_to_chunk(pos)

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
                faces[face.index] = False
            else:
                block = chunk.get_block(pos)

                faces[face.index] = block is None or (
                    not isinstance(block, str)
                    and (
                        not block.face_solid & face.invert().bitflag
                        or not instance.face_solid & face.bitflag
                    )
                )

        return faces

    @builtins_are_static()
    @name_is_static("EnumSide", lambda: EnumSide)
    @name_is_static("position_to_chunk", lambda: position_to_chunk)
    def exposed_faces_flag(self, block: str | Block.AbstractBlock | None) -> int:

        if block is None or isinstance(block, str):
            return 0b111111

        faces = 0

        for face in EnumSide.iterate():
            pos = face.relative_offset(block.position)
            chunk_position = position_to_chunk(pos)

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
                new_block = chunk.get_block(pos)

                if new_block is None or (
                    not isinstance(new_block, str)
                    and (
                        not new_block.face_solid & face.invert().bitflag
                        or not new_block.face_solid & face.bitflag
                    )
                ):
                    faces ^= face.bitflag

        return faces

    @builtins_are_static()
    @name_is_static("EnumSide", lambda: EnumSide)
    def exposed_faces_iterator(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Iterator[EnumSide]:
        instance = self.get_block(position, none_if_str=True)

        if instance is None:
            yield from EnumSide.iterate()
            return

        for face in EnumSide.iterate():
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
                            not block.face_solid & face.invert().bitflag
                            or not instance.face_solid & face.bitflag
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
        return position in self._world or (
            shared.world_generation_handler is not None
            and shared.world_generation_handler.task_handler.get_block(position, self)
            is not None
        )

    @deprecation.deprecated()
    def add_block_unsafe(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(
            self.add_block(*args, **kwargs)
        )

    @builtins_are_static()
    @name_is_static("normalize", lambda: normalize)
    async def add_block(
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
        network_sync=True,
    ):
        """
        Adds a block (given by name or a block instance) to the given position in this chunk

        :param position: the position to add
        :param block_name: the name of the block or an instance of it
        :param immediate: if the block should be shown if needed
        :param block_update: if an block-update should be sent to neighbor blocks
        :param block_update_self: if the block should get an block-update
        :param lazy_setup: a callable for setting up the block instance
        :param check_build_range: if the build limits should be checked
        :param block_state: the block state to create in, or None if not set
        :param replace_existing: if existing blocks should be replaced
        :param network_sync: do network sync or not
        :return: the block instance or None if it could not be created
        """
        # check if it is in build range
        r = self.dimension.get_world_height_range()
        if check_build_range and (position[1] < r[0] or position[1] > r[1]):
            return

        if position != normalize(position):
            raise ValueError(
                "position '{}' is no valid block position".format(position)
            )

        if position in self._world:
            if not replace_existing:
                return

            await self.remove_block(
                position,
                immediate=immediate,
                block_update=block_update,
                block_update_self=block_update_self,
                network_sync=network_sync,
            )

        if block_name in [None, "air", "minecraft:air"]:
            return

        if isinstance(block_name, Block.AbstractBlock):
            block = block_name
            block.position = position
            block.dimension = self.dimension.get_name()

            if lazy_setup is not None:
                result = lazy_setup(block)
                if isinstance(result, typing.Awaitable):
                    await result

            if shared.IS_CLIENT:
                block.face_info.update()

        # Create the block instance from the registry
        else:
            # todo: do we want to give a warning in the log?
            if not self.BLOCK_REGISTRY.is_valid_key(block_name):
                return

            block_cls = self.BLOCK_REGISTRY.get(block_name)

            block = block_cls()
            block.position = position
            block.dimension = self.dimension.get_name()
            if lazy_setup is not None:
                result = lazy_setup(block)

                if isinstance(result, typing.Awaitable):
                    await result

        # store the block instance in the local world
        self._world[position] = block

        await block.on_block_added()

        if block_state is not None:
            await block.set_model_state(block_state)

        self.mark_dirty()
        self.mark_position_dirty(position)

        if immediate and shared.IS_CLIENT:
            block.face_info.update()

            if block_update:
                await self.on_block_updated(position, include_itself=block_update_self)

            self.check_neighbors(position)

        return block

    @builtins_are_static()
    @object_method_is_protected("append", lambda: list.append)
    @name_is_static("EnumSide", lambda: EnumSide)
    async def on_block_updated(
        self, position: typing.Tuple[int, int, int], include_itself=True
    ):
        """
        Will call to the neighbor blocks a block update

        :param position: the position in the center
        :param include_itself: if the block itself (the block at 'position') should be updated
        """
        to_invoke = []
        x, y, z = position
        for face in EnumSide.iterate():
            b: Block.AbstractBlock = self.dimension.get_block(
                (x + face.dx, y + face.dy, z + face.dz), none_if_str=True
            )
            if b:
                to_invoke.append(b.on_block_update())

        if include_itself:
            b = self.get_block(position)
            if b:
                to_invoke.append(b.on_block_update())

        await asyncio.gather(*to_invoke)

    @builtins_are_static()
    @object_method_is_protected("Block", lambda: Block)
    async def remove_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        network_sync=True,
        reason=mcpython.util.enums.BlockRemovalReason.UNKNOWN,
    ):
        """
        Remove the block at the given position. When no block is there, nothing happens

        :param position: The (x, y, z) position of the block to remove, or the block instance
        :param immediate: Whether or not to immediately remove block from canvas.
        :param block_update: Whether an block-update should be called or not
        :param block_update_self: Whether the block to remove should get an block-update or not
        :param reason: the reason why the block was removed
        :param network_sync: if to send an update over the network or not
        todo: remove from scheduled world generation if needed
        """
        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        if position not in self._world:
            return

        await self._world[position].on_block_remove(reason)

        if shared.IS_CLIENT:
            self._world[position].face_info.hide_all()

        del self._world[position]

        if block_update:
            try:
                await self.on_block_updated(position, include_itself=block_update_self)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:  # lgtm [py/catch-base-exception]
                logger.println("during calling block update")

        if immediate:
            self.check_neighbors(position)

        self.mark_position_dirty(position)
        self.mark_dirty()

    @builtins_are_static()
    @name_is_static("EnmSide", lambda: EnumSide)
    @name_is_static("shared", lambda: shared)
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
        for face in EnumSide.iterate():
            block = self.dimension.get_block(
                face.relative_offset(position), none_if_str=True
            )
            if block is None:
                continue

            block.face_info.update(True)

    @builtins_are_static()
    @name_is_static("Block", lambda: Block)
    @name_is_static("shared", lambda: shared)
    def show_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
    ):
        """
        Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        :param position: The (x, y, z) position of the block to show.
        :param immediate: Whether to show the block immediately or not
        """
        if not shared.IS_CLIENT:
            return

        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        if position not in self._world:
            return

        if immediate:
            self._world[position].face_info.update(redraw_complete=True)
        else:
            shared.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

        self.mark_dirty()

    @builtins_are_static()
    @name_is_static("Block", lambda: Block)
    @name_is_static("shared", lambda: shared)
    def hide_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate=True,
    ):
        """
        Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        :param position: The (x, y, z) position of the block to hide.
        :param immediate: Whether to immediately remove the block from the canvas or not.
        """
        if not shared.IS_CLIENT:
            return

        if issubclass(type(position), Block.AbstractBlock):
            position = position.position

        if immediate:
            if position not in self._world:
                return
            self._world[position].face_info.hide_all()
        else:
            shared.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

        self.mark_dirty()

    @name_is_static("shared", lambda: shared)
    def show(self, force=False):
        """
        Will show the chunk

        :param force: if the chunk show should be forced or not
        """
        if not shared.IS_CLIENT:
            return

        if self.visible and not force:
            return

        self.visible = True
        self.update_visible()
        self.mark_dirty()

    @name_is_static("shared", lambda: shared)
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

    @name_is_static("shared", lambda: shared)
    def is_visible(self) -> bool:
        return self.visible and shared.IS_CLIENT

    @name_is_static("shared", lambda: shared)
    def update_visible_block(self, position: typing.Tuple[int, int, int], hide=True):
        if not shared.IS_CLIENT:
            return

        self.mark_position_dirty(position)

        if not self.exposed(position):
            self.hide_block(position)
        elif hide:
            self.show_block(position)

    @builtins_are_static()
    def exposed(self, position: typing.Tuple[int, int, int]) -> bool:
        return any(self.exposed_faces(position).values())

    @object_method_is_protected("keys", lambda: dict.keys)
    @name_is_static("shared", lambda: shared)
    def update_visible(self, hide=True, immediate=False):
        """
        Will update all visible of all blocks of the chunk

        :param hide: if blocks should be hidden if needed
        :param immediate: if immediate call or not
        """
        if not shared.IS_CLIENT:
            return

        if immediate:
            for position in self._world.keys():
                shared.world_generation_handler.task_handler.schedule_visual_update(
                    self, position
                )

        else:
            for position in self._world.keys():
                self.update_visible_block(position, hide=hide)

    @name_is_static("shared", lambda: shared)
    def hide_all(self, immediate=True):
        """
        Will hide all blocks in the chunk

        :param immediate: if immediate or not
        """
        if not shared.IS_CLIENT:
            return

        for position in self._world:
            self.hide_block(position, immediate=immediate)

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=True
    ) -> typing.Union[Block.AbstractBlock, str, None]:
        """
        Will get the block at an given position

        :param position: the position to check for, must be normalized
        :param none_if_str: if none if the block instance is str, defaults to True
        :return: None if no block, str if scheduled and Block.Block if created

        todo: split up into get_block[_generated] and get_block_un_generated
        """
        return (
            self._world[position]
            if position in self._world
            else (
                shared.world_generation_handler.task_handler.get_block(
                    position, chunk=self
                )
                if not none_if_str and shared.world_generation_handler is not None
                else None
            )
        )

    def __str__(self):
        return "Chunk(dimension={},position={})".format(
            self.dimension.get_dimension_id(), self.position
        )

    def is_loaded(self) -> bool:
        return self.loaded

    def is_generated(self) -> bool:
        return self.generated

    def get_entities(self):
        return self.entities

    @object_method_is_protected("format", lambda: str.format)
    @object_method_is_protected("values", lambda: dict.values)
    def dump_debug_maps(self, file_formatter: str):
        for m in self.data_maps.values():
            m.dump_debug_info(file_formatter.format(m.NAME.replace(":", "_")))

    def spawn_itemstack_in_world(
        self,
        itemstack: ItemStack,
        position: typing.Tuple[float, float, float],
        pickup_delay=0,
    ):
        entity = ItemEntity.create_new_entity(
            position,
            dimension=self.dimension,
            representing_item_stack=itemstack,
            pickup_delay=pickup_delay,
        )
        shared.entity_manager.spawn_entity(entity, position)
