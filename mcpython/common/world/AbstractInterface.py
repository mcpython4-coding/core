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
from abc import ABC
import typing
import enum
import mcpython.util.enums
import mcpython.server.worldgen.map.AbstractChunkInfoMap


class ChunkLoadTicketType(enum.Enum):
    SPAWN_CHUNKS = 0
    FORCE_LOADED = 1
    PLAYER_LOADED = 2  # needs player instance
    WORLD_GENERATION_LOADED = 3
    BLOCK_LOOKUP_LOADED = 4
    ENTITY_CHUNK_CHANGE_LOADED = 5
    ENTITY_AI_PROCESSING_LOADED = 6  # needs entity instance

    def __iter__(self):
        yield self


class ISupportWorldInterface(ABC):
    """
    Abstract intermediate common to chunk & dimension; Defines interaction with underlying world
    """

    def add_block(
        self,
        position: tuple,
        block_name: typing.Union[str, typing.Any],
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable[[typing.Any], None] = None,
        check_build_range=True,
        block_state=None,
    ) -> typing.Optional[typing.Any]:
        raise NotImplementedError

    def remove_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            typing.Any,
        ],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=None,
    ):
        raise NotImplementedError

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError

    def update_visible_block(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError

    def exposed(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[typing.Any, str, None]:
        raise NotImplementedError


class IChunk(ISupportWorldInterface, ABC):
    """
    Abstract class for chunks
    Belows follows an API description
    This API is STABLE, its implementation should NOT change dramatically if not needed
    Implementations beside the default Chunk implementation may change signature and calling type (async/await).
    They should try to be as close to the API as possible

    The following stuff MAY change in the near future:
        - structure / existence of __world-attribute
        - structure / existence of __positions_updated_since_last_save-attribute
        - existence of entities attribute
        - WIP of chunk_loaded_list attribute, together with add_chunk_load_ticket(...) and check_for_unload()
    """

    def __init__(self):
        # the world, as a dict position -> block instance
        # todo: use relative positions!
        # todo: maybe use sections -> dynamic based on world height?
        self._world: typing.Dict[typing.Tuple[int, int, int], typing.Any] = {}

        # set holding positions updated since last save
        # todo: use relative positions
        # todo: maybe replace by dirty sectors?
        self._positions_updated_since_last_save: typing.Set[
            typing.Tuple[int, int, int]
        ] = set()

        # a set of entities in this chunk
        # todo: maybe use per-sector?
        self.entities: typing.Set[typing.Any] = set()

        # inner API list for ChunkLoadTickets [WIP]
        # todo: use something better...
        self.chunk_loaded_list = tuple([[] for _ in range(16)])

        self.data_maps: typing.Dict[
            str, mcpython.server.worldgen.map.AbstractChunkInfoMap.AbstractMap
        ] = {}

    def clear(self):
        import mcpython.common.entity.PlayerEntity
        import mcpython.shared

        # So, we need to hide all blocks in this chunk for this to work...
        if mcpython.shared.IS_CLIENT:
            self.hide()

        self._world.clear()
        for entity in self.entities.copy():
            # We should not remove players...
            if not isinstance(entity, mcpython.common.entity.PlayerEntity.PlayerEntity):
                entity.kill(force=True)

    def get_map(self, name: str):
        return self.data_maps[name]

    def get_all_data_maps(self):
        return list(self.data_maps.values())

    def clear_positions_updated_since_last_save(self):
        self._positions_updated_since_last_save.clear()

    def get_positions_updated_since_last_save(self):
        return self._positions_updated_since_last_save

    def mark_position_dirty(self, position):
        self._positions_updated_since_last_save.add(position)
        self.mark_dirty()

    def is_loaded(self) -> bool:
        raise NotImplementedError

    def is_generated(self) -> bool:
        raise NotImplementedError

    def is_visible(self) -> bool:
        raise NotImplementedError

    def add_chunk_load_ticket(self, ticket_type: ChunkLoadTicketType, data=None):
        """
        Chunk load ticket API
        Adds a new ticket to the inner system for letting this chunk be loaded
        WIP
        todo: add timestamp
        todo: 16 lists are not good...
        todo: add way to remove ticket
        todo: save this to the save files
        """
        if ticket_type.value in (0, 1):
            assert data is None
            self.chunk_loaded_list[-1].append(ticket_type)
        elif ticket_type.value in (3, 4, 5, 6):
            assert data is None
            self.chunk_loaded_list[0].append(ticket_type)
        else:
            assert data is not None
            self.chunk_loaded_list[0].append((ticket_type, data))

    def check_for_unload(self):
        """
        Helper function for checking if this chunk should get unloaded or not
        todo: this is not optimal
        todo: do we really need to do this every tick?
        todo: 16 lists are bad!
        """
        flag = False
        for i, layer in enumerate(self.chunk_loaded_list):
            for ticket, *data in layer[:]:
                if ticket.value in (0, 1):
                    continue
                if (
                    ticket == ChunkLoadTicketType.PLAYER_LOADED
                ):  # check if player in range, if not, remove ticket
                    pass
                else:
                    layer.remove(ticket)
                    if i != 15:
                        self.chunk_loaded_list[i + 1].append(ticket)
            flag = flag or len(layer)
        if not flag:
            self.get_dimension().unload_chunk(self)

    def get_dimension(self) -> "IDimension":
        """
        Getter for the dimension of the chunk
        """
        raise NotImplementedError

    def get_position(self) -> typing.Tuple[int, int]:
        """
        Getter for the chunk position
        :return:
        """
        raise NotImplementedError

    def get_maximum_y_coordinate_from_generation(self, x: int, z: int) -> int:
        """
        Helper for finding the highest position in the chunk from generation
        todo: migrate to special system for world generation attributes
        """
        raise NotImplementedError

    def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[mcpython.util.enums.EnumSide, bool]:
        """
        Helper for getting exposed faces of a block
        todo: add iterating variant
        """
        raise NotImplementedError

    def is_position_blocked(self, position: typing.Tuple[float, float, float]) -> bool:
        """
        Checks if the given position is not air
        """
        raise NotImplementedError

    def add_block(
        self,
        position: tuple,
        block_name: typing.Union[str, typing.Any],
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable[[typing.Any], None] = None,
        check_build_range=True,
        block_state=None,
    ) -> typing.Optional[typing.Any]:
        """
        Adds an block to the given position
        :param position: the position to add at
        :param block_name: the name of the block or an instance of it (typing.Any)
        :param immediate: if the block should be shown if needed or not
        :param block_update: if an block-update should be send to neighbors blocks
        :param block_update_self: if the block should get an block-update
        :param lazy_setup: an callable for setting up the block instance
        :param check_build_range: if the build limits should be checked
        :param block_state: the block state to create in, or None if not set
        :return: the block instance or None if it could not be created for some reason
        todo: add method which raises an exception on fail
        """
        raise NotImplementedError

    def on_block_updated(
        self, position: typing.Tuple[float, float, float], itself=True
    ):
        """
        Updates the block at the given position
        """
        raise NotImplementedError

    def remove_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            typing.Any,
        ],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=None,
    ):
        """
        Removes a block from a given position
        :param position: the position to remove at
        :param immediate: immediate hide?
        :param block_update: block update to the blocks around?
        :param block_update_self: block update to the current block?
        :param reason: why it is removed, see mcpython.common.block.AbstractBlock.BlockRemovalReason for possible
            values
        todo: add "unsafe" variant skipping various sanity checks
        todo: add option to not call on_remove on target block
        """
        raise NotImplementedError

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        """
        Checks the visual state of adjusting blocks to the given position
        todo: rename to something fitting!
        """
        raise NotImplementedError

    def update_all_rendering(self):
        for position, block in self._world.items():
            if not self.exposed(position):
                block.face_state.hide_all()
            else:
                block.face_state.update()

    def show(self):
        """
        Shows the entire chunk
        """
        raise NotImplementedError

    def hide(self):
        """
        Hides an entire chunk
        :param force: if to force-hide
        """
        raise NotImplementedError

    def update_visible_block(self, position: typing.Tuple[int, int, int]):
        """
        Calls Block.face_state.update()
        :param position: the position to update at
        """
        raise NotImplementedError

    def exposed(self, position: typing.Tuple[int, int, int]):
        """
        Checks if the given position is exposed so it should be shown
        :param position: the position to check
        """
        raise NotImplementedError

    def update_visible(self, immediate=False):
        """
        Updates the visible state of ALL blocks in the chunk
        :param immediate: immediate execute tasks or scheduling for later?
        """
        raise NotImplementedError

    def hide_all(self, immediate=True):
        """
        Hides all chunks in the chunk
        :param immediate: immediate execute tasks or scheduling for later?
        """
        raise NotImplementedError

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[typing.Any, str, None]:
        """
        Getter function for a block
        :param position: the position
        :param none_if_str: if the block instance would be a str, replace it by None?
        :return: the block instance, a str representing a block (e.g. for scheduled during generation) or None
            if there is no block
        """
        raise NotImplementedError

    def as_shareable(self) -> "IChunk":
        """
        Creates a reference to this chunk which can be linked across threads / processes
        :return: this chunk instance
        INFO: currently not in use
        """
        raise NotImplementedError

    def mark_dirty(self):
        raise NotImplementedError

    def get_entities(self):
        raise NotImplementedError

    def tick(self):
        pass

    def save(self):
        pass

    def __getitem__(self, item):
        return self.get_block(item)

    def __setitem__(self, key, value):
        self.add_block(key, value)

    def __delitem__(self, key):
        self.remove_block(key)

    def __contains__(self, item):
        return self.get_block(item) is not None

    def __iter__(self):
        # todo: is there a better way?
        yield from self._world.items()

    def __eq__(self, other: "IChunk"):
        return (
            self.get_dimension() == other.get_dimension()
            and self.get_position() == other.get_position()
        )

    def __hash__(self):
        return hash((self.get_dimension().get_name(), self.get_position()))

    def entity_iterator(self) -> typing.Iterable:
        raise NotImplementedError


class IDimension(ISupportWorldInterface, ABC):
    def __init__(self):
        self.loaded = True

    def get_dimension_range(self) -> typing.Tuple[int, int]:
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError

    def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> IChunk:
        raise NotImplementedError

    def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            typing.Any,
        ],
        **kwargs
    ) -> typing.Optional[IChunk]:
        raise NotImplementedError

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[typing.Any, str, None]:
        raise NotImplementedError

    def add_block(
        self,
        position: tuple,
        block_name: str,
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable = None,
        check_build_range=True,
        block_state=None,
    ):
        raise NotImplementedError

    def remove_block(
        self, position: tuple, immediate=True, block_update=True, block_update_self=True
    ):
        raise NotImplementedError

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError

    def hide_block(self, position, immediate=True):
        raise NotImplementedError

    def get_world_generation_config_for_layer(self, layer_name: str):
        raise NotImplementedError

    def get_world_generation_config_entry(self, name: str, default=None):
        raise NotImplementedError

    def set_world_generation_config_entry(self, name: str, value):
        raise NotImplementedError

    def set_world_generation_config_for_layer(self, layer_name, layer_config):
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError

    def unload_chunk(self, chunk: IChunk):
        raise NotImplementedError

    def tick(self):
        pass

    def entity_iterator(self) -> typing.Iterable:
        raise NotImplementedError

    def get_world(self) -> "IDimension":
        raise NotImplementedError


class IWorld(ABC):
    def get_dimension_names(self) -> typing.Iterable[str]:
        raise NotImplementedError

    def add_player(
        self, name: str, add_inventories: bool = True, override: bool = True
    ):
        raise NotImplementedError

    def get_active_player(self, create: bool = True) -> typing.Optional:
        raise NotImplementedError

    def player_iterator(self) -> typing.Iterable:
        raise NotImplementedError

    def reset_config(self):
        raise NotImplementedError

    def get_active_dimension(self) -> typing.Union[IDimension, None]:
        raise NotImplementedError

    def add_dimension(self, dim_id: int, name: str, dim_config=None) -> IDimension:
        raise NotImplementedError

    def join_dimension(self, dim_id: int):
        raise NotImplementedError

    def get_dimension(self, dim_id: int) -> IDimension:
        raise NotImplementedError

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
        raise NotImplementedError

    def show_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError

    def hide_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError

    def change_chunks(
        self,
        before: typing.Union[typing.Tuple[int, int], None],
        after: typing.Union[typing.Tuple[int, int], None],
        generate_chunks=True,
        load_immediate=True,
    ):
        raise NotImplementedError

    def cleanup(self, remove_dims=False, filename=None):
        raise NotImplementedError

    def setup_by_filename(self, filename: str):
        raise NotImplementedError

    def entity_iterator(self) -> typing.Iterable:
        raise NotImplementedError
