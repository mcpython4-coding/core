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
import typing
from abc import ABC

import deprecation
import mcpython.common.event.api
import mcpython.util
import mcpython.util.enums
import pyglet
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class BlockStateNotNeeded(Exception):
    pass


@onlyInClient()
class IBlockStateRenderingTarget:
    NAME = None

    def __init__(self):
        self.block_state = None
        self.position = None
        self.face_info = None

    def get_model_state(self):
        pass

    def get_tint_for_index(
        self, index: int
    ) -> typing.Tuple[float, float, float, float]:
        return 1, 1, 1, 1


@onlyInClient()
class IBlockStateDecoder(mcpython.common.event.api.IRegistryContent, ABC):
    """
    Abstract base class for block state decoders

    Identification of files to decode:
        bool(is_valid(data)) == True, where data is the loaded json data
        for developers of mods: add an entry called "mod_marker" storing the mod name the loader is implemented in and
            check for it here

    Loading:
        __init__(data, BlockStateDefinition) -> Instance

    Baking:
        bake() is called to on_bake references and do similar stuff, returning success or not

    Drawing:
        add_face_to_batch() should add the given face to the batches given
        add_raw_face_to_batch() should add a face to the batch without the block instance, but instead the position
        draw() should draw the block in-place

    todo: cache non-offset data from models per state for faster drawing
    todo: can we do something rendering wise which will make it efficient to draw multiple same blocks
    todo: block batches should be selected before, based on a property on block class
    """

    TYPE = "minecraft:blockstate"

    __slots__ = ("data", "block_state")

    @classmethod
    def is_valid(cls, data: dict) -> bool:
        """
        Checker function if some data matches the loader
        """
        raise NotImplementedError

    def __init__(self, block_state):
        self.data = None
        self.block_state = block_state

    def parse_data(self, data: dict):
        raise NotImplementedError

    async def bake(self) -> bool:
        """
        Bake method for doing some stuff after loading all block-states
        :return: if successful or not
        """
        return True

    @deprecation.deprecated()
    def add_face_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        face: mcpython.util.enums.EnumSide,
    ) -> typing.Iterable:
        return tuple()

    def add_faces_to_batch(
        self,
        instance: IBlockStateRenderingTarget,
        batch: pyglet.graphics.Batch,
        faces: int,
    ) -> typing.Iterable:
        raise NotImplementedError()

    def add_raw_face_to_batch(
        self, instance: IBlockStateRenderingTarget, position, state, batches, faces
    ):
        return tuple()

    # optional: draws the BlockState direct without a batch
    def draw_face(
        self,
        instance: IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
    ):
        pass

    def draw_face_scaled(
        self,
        instance: IBlockStateRenderingTarget,
        face: mcpython.util.enums.EnumSide,
        scale: float,
    ):
        pass

    # optional: transforms the BlockState into an BoundingBox-like objects
    def transform_to_bounding_box(
        self,
        instance: IBlockStateRenderingTarget,
    ):
        pass


@onlyInClient()
class IItemModelLoader:
    @classmethod
    def validate(cls, data: dict) -> bool:
        raise NotImplementedError()

    @classmethod
    async def decode(cls, data: dict, model):
        raise NotImplementedError()


@onlyInClient()
class AbstractBoxModel(ABC):
    def copy(self) -> "AbstractBoxModel":
        raise NotImplementedError
