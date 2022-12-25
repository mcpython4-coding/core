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
from mcpython.engine.world.AbstractInterface import IWorld
from unittest import mock


class InventoryHandlerMockup:
    SHOWN = False

    @classmethod
    async def add(cls, inventory):
        return

    @classmethod
    async def show(cls, inventory):
        cls.SHOWN = True


class CraftingHandlerMockup:
    def __call__(self, *args, **kwargs):
        return args[0]


def WorldMockup() -> IWorld:
    world_mock = mock.Mock(IWorld)
    world_mock.entities = set()
    world_mock.dimension = None
    world_mock.position = None
    world_mock.dimension = world_mock
    world_mock.get_dimension_by_name = world_mock.get_chunk_for_position = mock.Mock(return_value=world_mock)
    world_mock.exposed_faces = mock.Mock(side_effect=lambda: dict())
    world_mock.exposed_faces_list = mock.Mock(side_effect=lambda: [False] * 6)
    world_mock.exposed_faces_flag = mock.Mock(return_value=0)
    world_mock.get_name = mock.Mock(return_value="overworld")
    world_mock.get_dimension_id = mock.Mock(return_value=0)
    world_mock.get_active_dimension = world_mock.get_dimension = mock.Mock(return_value=world_mock)

    return world_mock
