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
import itertools
import os
import typing

import mcpython.common.block.AbstractBlock
import mcpython.common.world.Chunk
import mcpython.engine.rendering.util
import mcpython.engine.world.AbstractInterface
import mcpython.util.math
import pyglet

from bytecodemanipulation.Optimiser import cache_global_name
from bytecodemanipulation.Optimiser import guarantee_builtin_names_are_protected
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.common.entity.ItemEntity import ItemEntity


class DimensionDefinition:
    """
    class for an dimension placeholder
    """

    def __init__(self, name: str, config: dict):
        """
        will create an new placeholder
        WARNING: must be send to shared.dimension_handler
        :param name: the dimension name
        :param config: the config for it
        """
        self.name = name
        self.id = None
        self.config = config

    def setStaticId(self, dim_id: int):
        """
        will set the id of the dimension (when static)
        :param dim_id: the id for the dimension
        :return: self
        """
        self.id = dim_id
        return self


class DimensionHandler:
    """
    Handler for the dimensions
    Works together with the World-class in handling the system
    This class holds general data about the status of the game dimensions, not for an world instance
    todo: make it fully data-driven
    """

    def __init__(self):
        self.dimensions = {}
        self.unfinished_dims = []

        from mcpython.common.mod.ModMcpython import mcpython

        mcpython.eventbus.subscribe("stage:post", self.finish())

    async def finish(self):
        """
        Called to finish up and assign ids to dynamic dimensions
        """
        i = 0
        for dim in self.unfinished_dims:
            while i in self.unfinished_dims:
                i += 1
            dim.id = i
            self.add_dimension(dim)

    async def add_default_dimensions(self):
        """
        Implementation for mcpython: will add the dimensions used by the core into the system
        """
        self.add_dimension(
            DimensionDefinition(
                "minecraft:overworld",
                {"configname": "minecraft:default_overworld"},
            ).setStaticId(0)
        )
        self.add_dimension(
            DimensionDefinition(
                "minecraft:the_nether", {"configname": "minecraft:nether_generator"}
            ).setStaticId(-1)
        )
        self.add_dimension(
            DimensionDefinition("minecraft:the_end", {"configname": None}).setStaticId(
                1
            )
        )

    def add_dimension(self, dim: DimensionDefinition):
        """
        Will add an new dimension definition into the system
        :param dim: the dimension definition to add
        """
        if dim.id is None:
            self.unfinished_dims.append(dim)
        else:
            self.dimensions[dim.id] = dim

    def init_dims(self):
        """
        Will create all dimension in the active world
        """
        for dim in self.dimensions.values():
            shared.world.add_dimension(dim.id, dim.name, dim_config=dim.config)


shared.dimension_handler = DimensionHandler()


if not shared.IS_TEST_ENV:
    from mcpython.common.mod.ModMcpython import mcpython as mc

    mc.eventbus.subscribe(
        "stage:dimension", shared.dimension_handler.add_default_dimensions()
    )


class Dimension(mcpython.engine.world.AbstractInterface.IDimension):
    """
    Class holding a whole dimension
    Default cross-side implementation

    todo: add save/load/delete methods
    todo: better config system for world gen
    todo: move rendering to separated structure only created on client!
    """

    # normal, alpha; mods are free to add more; todo: add better API
    BATCH_COUNT = 2

    @guarantee_builtin_names_are_protected()
    def __init__(
        self,
        world_in: mcpython.engine.world.AbstractInterface.IWorld,
        dim_id: int,
        name: str,
        gen_config=None,
    ):
        """
        Creates a new dimension. Should be registered to the world instance.
        Can be automated by using the appropriate function at world
        :param world_in: the world instance to use
        :param dim_id: the id for it
        :param name: the name for it
        :param gen_config: the config to use for generation
        """
        super().__init__()
        if gen_config is None:
            gen_config = {}

        self.id = dim_id
        self.world = world_in
        self.chunks: typing.Dict[
            typing.Tuple[int, int], mcpython.engine.world.AbstractInterface.IChunk
        ] = {}

        self.name = name
        self.world_generation_config = gen_config
        self.world_generation_config_objects = {}

        # batches, see above for usages
        self.batches = [pyglet.graphics.Batch() for _ in range(self.BATCH_COUNT)]

        self.height_range = (0, 255)

    @guarantee_builtin_names_are_protected()
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
            chunk = self.get_chunk(*chunk, generate=False)

        if chunk is None:
            return

        chunk.show()

    @guarantee_builtin_names_are_protected()
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
            chunk = self.get_chunk(*chunk, generate=False)

        if chunk is None:
            return

        chunk.hide()

    def update_visible_block(self, position: typing.Tuple[int, int, int]):
        self.get_chunk_for_position(position, generate=False).update_visible_block(
            position
        )

    def exposed(self, position: typing.Tuple[int, int, int]):
        return self.get_chunk_for_position(position, generate=False).exposed(position)

    def get_world(self):
        return self.world

    def entity_iterator(self) -> typing.Iterable:
        for chunk in self.chunks.values():
            yield from chunk.entity_iterator()

    def tick(self):
        for chunk in self.chunks.values():
            if chunk.is_loaded():
                chunk.tick()

    def unload_chunk(self, chunk: mcpython.engine.world.AbstractInterface.IChunk):
        chunk.save()
        chunk.hide_all(True)
        del self.chunks[chunk.get_position()]

    def get_world_height_range(self) -> typing.Tuple[int, int]:
        return self.height_range

    def get_dimension_id(self):
        return self.id

    @guarantee_builtin_names_are_protected()
    def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> typing.Optional[mcpython.engine.world.AbstractInterface.IChunk]:
        """
        Used to get a chunk instance with a given chunk-position
        :param cx: the chunk x position or a tuple of (x, z)
        :param cz: the chunk z position or None íf cx is a tuple
        :param generate: if the chunk should be scheduled for generation if it is not generated
        :param create: if the chunk instance should be created when it does not exist
        :return: the chunk instance or None
        :raises ValueError: if cz is None and cx is now tuple
        """
        if cz is None:
            if type(cx) != tuple:
                raise ValueError

            cx, cz = cx

        if (cx, cz) not in self.chunks:
            if not create:
                return

            self.chunks[(cx, cz)] = mcpython.common.world.Chunk.Chunk(self, (cx, cz))

            if generate:
                shared.world_generation_handler.add_chunk_to_generation_list(
                    self.chunks[(cx, cz)]
                )

        return self.chunks[(cx, cz)]

    @guarantee_builtin_names_are_protected()
    def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        **kwargs,
    ) -> typing.Optional[mcpython.engine.world.AbstractInterface.IChunk]:
        """
        Gets a chunk for a block-position
        :param position: the position to use or the block instance to use
        :param kwargs: same as get_chunk()
        :return: the chunk instance or None
        :raises: ValueError: if position is not tuple or block
        """
        if issubclass(
            type(position), mcpython.common.block.AbstractBlock.AbstractBlock
        ):
            position = position.position
        elif not isinstance(position, tuple):
            raise ValueError(position)

        return self.get_chunk(mcpython.util.math.position_to_chunk(position), **kwargs)

    def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        chunk = self.get_chunk_for_position(position, generate=False, create=False)
        if chunk is None:
            return

        return chunk.get_block(position, none_if_str=none_if_str)

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
        network_sync=True,
    ):
        chunk = self.get_chunk_for_position(position, generate=False)
        return chunk.add_block(
            position,
            block_name,
            immediate=immediate,
            block_update=block_update,
            block_update_self=block_update_self,
            lazy_setup=lazy_setup,
            check_build_range=check_build_range,
            block_state=block_state,
            network_sync=network_sync,
        )

    async def remove_block(
        self,
        position: tuple,
        immediate=True,
        block_update=True,
        block_update_self=True,
        network_sync=True,
    ):
        chunk = self.get_chunk_for_position(position)
        await chunk.remove_block(
            position,
            immediate=immediate,
            block_update=block_update,
            block_update_self=block_update_self,
            network_sync=network_sync,
        )

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        self.get_chunk_for_position(position).check_neighbors(position)

    def show_block(self, position, immediate=True):
        self.get_chunk_for_position(position).show_block(position, immediate=immediate)

    def hide_block(self, position, immediate=True):
        self.get_chunk_for_position(position).hide_block(position, immediate=immediate)

    @guarantee_builtin_names_are_protected()
    def draw(self):
        self.batches[0].draw()

        shared.rendering_helper.enableAlpha()
        self.batches[1].draw()

        x, z = mcpython.util.math.position_to_chunk(
            shared.world.get_active_player().position
        )
        pad = 4

        for dx, dz in itertools.product(range(-pad, pad + 1), repeat=2):
            cx, cz = x + dx, z + dz
            chunk = self.get_chunk(cx, cz, create=False)
            if chunk is not None and isinstance(
                chunk, mcpython.common.world.Chunk.Chunk
            ):
                chunk.draw()

        shared.rendering_helper.disableAlpha()

    def __del__(self):
        self.chunks.clear()
        del self.world
        self.world_generation_config_objects.clear()
        self.batches.clear()

    def get_world_generation_config_for_layer(self, layer_name: str):
        return self.world_generation_config_objects[layer_name]

    def set_world_generation_config_for_layer(self, layer_name, layer_config):
        self.world_generation_config_objects[layer_name] = layer_config

    def get_world_generation_config_entry(self, name: str, default=None):
        return (
            self.world_generation_config[name]
            if name in self.world_generation_config
            else default
        )

    def set_world_generation_config_entry(self, name: str, value):
        self.world_generation_config[name] = value

    def get_name(self) -> str:
        return self.name

    @cache_global_name("os", lambda: os)
    def dump_debug_maps_all_chunks(self, file_formatter: str):
        os.makedirs(os.path.dirname(file_formatter.format("test")), exist_ok=True)
        for pos, chunk in self.chunks.items():
            chunk.dump_debug_maps(file_formatter.format(f"{pos[0]}_{pos[1]}_{{}}"))

    def chunk_iterator(self):
        return self.chunks.values()

    @cache_global_name("shared", lambda: shared)
    @cache_global_name("ItemEntity", lambda: ItemEntity)
    def spawn_itemstack_in_world(
        self,
        itemstack: ItemStack,
        position: typing.Tuple[float, float, float],
        pickup_delay=0,
    ):
        if itemstack.is_empty():
            return

        entity = ItemEntity.create_new_entity(
            position,
            dimension=self,
            representing_item_stack=itemstack,
            pickup_delay=pickup_delay,
        )
        shared.entity_manager.spawn_entity(entity, position)
