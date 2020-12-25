"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import sys
import typing

import deprecation
import pyglet

from mcpython import shared as G
import mcpython.common.block.AbstractBlock
import mcpython.common.mod.ModMcpython
import mcpython.client.rendering.util
import mcpython.util.math
import mcpython.common.world.Chunk
import mcpython.common.world.AbstractInterface


class DimensionDefinition:
    """
    class for an dimension placeholder
    """

    def __init__(self, name: str, config: dict):
        """
        will create an new placeholder
        WARNING: must be send to G.dimensionhandler
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
    """

    def __init__(self):
        self.dimensions = {}
        self.unfinished_dims = []
        mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
            "stage:post", self.finish
        )

    def finish(self):
        """
        called to finish up and assign ids to dynamic dimensions
        """
        i = 0
        for dim in self.unfinished_dims:
            while i in self.unfinished_dims:
                i += 1
            dim.id = i
            self.add_dimension(dim)

    def add_default_dimensions(self):
        """
        implementation for mcpython: will add the dimensions used by the core into the system
        """
        self.add_dimension(
            DimensionDefinition(
                "minecraft:overworld",
                {"configname": ("minecraft:default_overworld")},
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
        will add an new dimension definition into the system
        :param dim: the dimension defintion to add
        """
        if dim.id is None:
            self.unfinished_dims.append(dim)
        else:
            self.dimensions[dim.id] = dim

    def init_dims(self):
        """
        will create all dimension in the active world
        """
        for dim in self.dimensions.values():
            G.world.add_dimension(dim.id, dim.name, dim_config=dim.config)


G.dimension_handler = DimensionHandler()

mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:dimension", G.dimension_handler.add_default_dimensions
)


class Dimension(mcpython.common.world.AbstractInterface.IDimension):
    """
    Class holding an whole dimension
    """

    BATCH_COUNT = 2  # normal, alpha; mods are free to add more

    def __init__(self, world_in, dim_id: int, name: str, gen_config=None):
        """
        Creates an new dimension. Must be send also to the World-instance
        :param world_in: the world instance to use
        :param dim_id: the id for it
        :param name: the name for it
        :param gen_config: the config to use for generation
        """
        if gen_config is None:
            gen_config = {}
        self.id = dim_id
        self.world = world_in
        self.chunks: typing.Dict[
            typing.Tuple[int, int], mcpython.common.world.AbstractInterface.IChunk
        ] = {}
        self.name = name
        self.world_generation_config = gen_config
        self.world_generation_config_objects = {}
        # normal batch
        self.batches = [pyglet.graphics.Batch() for _ in range(self.BATCH_COUNT)]

        self.height_range = (0, 255)

    def get_dimension_range(self) -> typing.Tuple[int, int]:
        return self.height_range

    def get_id(self):
        return self.id

    def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> typing.Optional[mcpython.common.world.AbstractInterface.IChunk]:
        """
        used to get an chunk instance with an given position
        :param cx: the chunk x position or an tuple of (x, z)
        :param cz: the chunk z position or None íf cx is tuple
        :param generate: if the chunk should be scheduled for generation if it is not generated
        :param create: if the chunk instance should be created when it does not exist
        :return: the chunk instance or None
        """
        if cz is None:
            assert type(cx) == tuple
            cx, cz = cx

        if (cx, cz) not in self.chunks:
            if not create:
                return
            self.chunks[(cx, cz)] = mcpython.common.world.Chunk.Chunk(self, (cx, cz))
            if generate:
                G.world_generation_handler.add_chunk_to_generation_list(
                    self.chunks[(cx, cz)]
                )

        return self.chunks[(cx, cz)]

    def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        **kwargs
    ) -> typing.Optional[mcpython.common.world.AbstractInterface.IChunk]:
        """
        gets an chunk for an position
        :param position: the position to use or the block instance to use
        :param kwargs: same as get_chunk()
        :return: the chunk instance or None
        """
        if issubclass(
            type(position), mcpython.common.block.AbstractBlock.AbstractBlock
        ):
            position = position.position

        return self.get_chunk(*mcpython.util.math.positionToChunk(position), **kwargs)

    @deprecation.deprecated()
    def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        chunk = self.get_chunk_for_position(position, generate=False, create=False)
        if chunk is None:
            return

        return chunk.get_block(position)

    @deprecation.deprecated()
    def add_block(
        self,
        position: tuple,
        block_name: str,
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable = None,
        check_build_range=True,
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
        )

    @deprecation.deprecated()
    def remove_block(
        self, position: tuple, immediate=True, block_update=True, block_update_self=True
    ):
        chunk = self.get_chunk_for_position(position)
        chunk.remove_block(
            position,
            immediate=immediate,
            block_update=block_update,
            block_update_self=block_update_self,
        )

    @deprecation.deprecated()
    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        self.get_chunk_for_position(position).check_neighbors(position)

    @deprecation.deprecated()
    def show_block(self, position, immediate=True):
        self.get_chunk_for_position(position).show_block(position, immediate=immediate)

    @deprecation.deprecated()
    def hide_block(self, position, immediate=True):
        self.get_chunk_for_position(position).hide_block(position, immediate=immediate)

    def draw(self):
        self.batches[0].draw()

        G.rendering_helper.enableAlpha()
        self.batches[1].draw()

        x, z = mcpython.util.math.positionToChunk(G.world.get_active_player().position)
        pad = 4
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                cx, cz = x + dx, z + dz
                chunk = self.get_chunk(cx, cz, create=False)
                if chunk is not None and isinstance(
                    chunk, mcpython.common.world.Chunk.Chunk
                ):
                    chunk.draw()

        G.rendering_helper.disableAlpha()

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
