"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.world.AbstractInterface
import mcpython.util
from mcpython.common.world.AbstractInterface import IChunk
import mcpython.common.block.AbstractBlock
import mcpython.util.enums


class RemoteWorld(mcpython.common.world.AbstractInterface.IWorld):
    async def get_dimension_names(self) -> typing.Iterable[str]:
        pass

    async def add_player(
        self, name: str, add_inventories: bool = True, override: bool = True
    ):
        pass

    async def get_active_player(self, create: bool = True) -> typing.Optional:
        pass

    async def reset_config(self):
        pass

    async def get_active_dimension(self) -> typing.Union["RemoteDimension", None]:
        pass

    async def add_dimension(
        self, dim_id: int, name: str, dim_config=None
    ) -> "RemoteDimension":
        pass

    async def join_dimension(self, dim_id: int):
        pass

    async def get_dimension(self, dim_id: int) -> "RemoteDimension":
        pass

    async def hit_test(
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
        pass

    async def show_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        pass

    async def hide_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        pass

    async def change_chunks(
        self,
        before: typing.Union[typing.Tuple[int, int], None],
        after: typing.Union[typing.Tuple[int, int], None],
        generate_chunks=True,
        load_immediate=True,
    ):
        pass

    async def cleanup(self, remove_dims=False, filename=None):
        pass

    async def setup_by_filename(self, filename: str):
        pass


class RemoteDimension(mcpython.common.world.AbstractInterface.IDimension):
    def get_dimension_range(self) -> typing.Tuple[int, int]:
        pass

    def get_id(self):
        pass

    def get_name(self) -> str:
        pass

    async def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> IChunk:
        pass

    async def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        **kwargs
    ) -> typing.Optional[IChunk]:
        pass

    async def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        pass

    async def add_block(
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
        pass

    async def remove_block(
        self, position: tuple, immediate=True, block_update=True, block_update_self=True
    ):
        pass

    async def check_neighbors(self, position: typing.Tuple[int, int, int]):
        pass

    async def hide_block(self, position, immediate=True):
        pass

    async def get_world_generation_config_for_layer(self, layer_name: str):
        pass

    async def get_world_generation_config_entry(self, name: str, default=None):
        pass

    async def set_world_generation_config_entry(self, name: str, value):
        pass

    async def set_world_generation_config_for_layer(self, layer_name, layer_config):
        pass

    async def unload_chunk(self, chunk: IChunk):
        pass


class RemoteChunk(mcpython.common.world.AbstractInterface.IChunk):
    def is_loaded(self) -> bool:
        pass

    def is_generated(self) -> bool:
        pass

    def is_visible(self) -> bool:
        pass

    def get_dimension(self) -> "RemoteDimension":
        pass

    def get_position(self) -> typing.Tuple[int, int]:
        pass

    async def get_maximum_y_coordinate_from_generation(self, x: int, z: int) -> int:
        pass

    async def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[mcpython.util.enums.EnumSide, bool]:
        pass

    async def is_position_blocked(
        self, position: typing.Tuple[float, float, float]
    ) -> bool:
        pass

    async def add_block(
        self,
        position: tuple,
        block_name: typing.Union[
            str, mcpython.common.block.AbstractBlock.AbstractBlock
        ],
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable[
            [mcpython.common.block.AbstractBlock.AbstractBlock], None
        ] = None,
        check_build_range=True,
        block_state=None,
    ) -> typing.Optional[mcpython.common.block.AbstractBlock.AbstractBlock]:
        pass

    async def on_block_updated(
        self, position: typing.Tuple[float, float, float], itself=True
    ):
        pass

    async def remove_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=mcpython.common.block.AbstractBlock.BlockRemovalReason.UNKNOWN,
    ):
        pass

    async def check_neighbors(self, position: typing.Tuple[int, int, int]):
        pass

    async def show_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate: bool = True,
    ):
        pass

    async def hide_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate=True,
    ):
        pass

    async def show(self, force=False):
        pass

    async def hide(self, force=False):
        pass

    async def update_visible_block(
        self, position: typing.Tuple[int, int, int], hide=True
    ):
        pass

    async def exposed(self, position: typing.Tuple[int, int, int]):
        pass

    async def update_visible(self, hide=True, immediate=False):
        pass

    async def hide_all(self, immediate=True):
        pass

    async def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        pass

    async def as_shareable(self) -> "RemoteChunk":
        pass

    async def mark_dirty(self):
        pass

    async def get_entities(self):
        pass

    async def set_value(self, key: str, data):
        pass

    async def get_value(self, key: str):
        pass
