"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from abc import ABC
import typing
import mcpython.util.enums
import mcpython.common.block.AbstractBlock


class IChunk(ABC):
    def get_dimension(self) -> "IDimension":
        raise NotImplementedError()

    def get_position(self) -> typing.Tuple[int, int]:
        raise NotImplementedError()

    def get_maximum_y_coordinate_from_generation(self, x: int, z: int) -> int:
        raise NotImplementedError()

    def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[mcpython.util.enums.EnumSide, bool]:
        raise NotImplementedError()

    def is_position_blocked(self, position: typing.Tuple[float, float, float]) -> bool:
        raise NotImplementedError()

    def add_block(
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
    ):
        raise NotImplementedError()

    def on_block_updated(
        self, position: typing.Tuple[float, float, float], itself=True
    ):
        raise NotImplementedError()

    def remove_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=mcpython.common.block.AbstractBlock.BlockRemovalReason.UNSET,
    ):
        raise NotImplementedError()

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError()

    def show_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate: bool = True,
    ):
        raise NotImplementedError()

    def hide_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        immediate=True,
    ):
        raise NotImplementedError()

    def show(self, force=False):
        raise NotImplementedError()

    def hide(self, force=False):
        raise NotImplementedError()

    def update_visible_block(self, position: typing.Tuple[int, int, int], hide=True):
        raise NotImplementedError()

    def exposed(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError()

    def update_visible(self, hide=True, immediate=False):
        raise NotImplementedError()

    def hide_all(self, immediate=True):
        raise NotImplementedError()

    def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        raise NotImplementedError()


class IDimension(ABC):
    def get_id(self):
        raise NotImplementedError()

    def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> IChunk:
        raise NotImplementedError()

    def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            mcpython.common.block.AbstractBlock.AbstractBlock,
        ],
        **kwargs
    ) -> typing.Optional[IChunk]:
        raise NotImplementedError()

    def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[mcpython.common.block.AbstractBlock.AbstractBlock, str, None]:
        raise NotImplementedError()

    def add_block(
        self,
        position: tuple,
        block_name: str,
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable = None,
    ):
        raise NotImplementedError()

    def remove_block(
        self, position: tuple, immediate=True, block_update=True, block_update_self=True
    ):
        raise NotImplementedError()

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        raise NotImplementedError()

    def hide_block(self, position, immediate=True):
        raise NotImplementedError()


class IWorld(ABC):
    def add_player(
        self, name: str, add_inventories: bool = True, override: bool = True
    ):
        raise NotImplementedError()

    def get_active_player(self, create: bool = True) -> typing.Optional:
        raise NotImplementedError()

    def reset_config(self):
        raise NotImplementedError()

    def get_active_dimension(self) -> typing.Union[IDimension, None]:
        raise NotImplementedError()

    def add_dimension(
        self, dim_id: int, name: str, dim_config=None, config=None
    ) -> IDimension:
        raise NotImplementedError()

    def join_dimension(self, dim_id: int):
        raise NotImplementedError()

    def get_dimension(self, dim_id: int) -> IDimension:
        raise NotImplementedError()

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
        raise NotImplementedError()

    def show_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError()

    def hide_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError()

    def change_chunks(
        self,
        before: typing.Union[typing.Tuple[int, int], None],
        after: typing.Union[typing.Tuple[int, int], None],
        generate_chunks=True,
        load_immediate=True,
    ):
        raise NotImplementedError()

    def cleanup(self, remove_dims=False, filename=None):
        raise NotImplementedError()

    def setup_by_filename(self, filename: str):
        raise NotImplementedError()
