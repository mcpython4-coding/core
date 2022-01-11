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

from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from tests.util import TestCase

shared.IS_TEST_ENV = True

from mcpython.server.worldgen.map.BiomeMap import BiomeMap
from mcpython.server.worldgen.map.FeatureMap import FeatureMap
from mcpython.server.worldgen.map.HeightMap import HeightMap
from mcpython.server.worldgen.map.LandMassMap import LandMassMap
from mcpython.server.worldgen.map.TemperatureMap import TemperatureMap


class FakeChunk:
    def __init__(self, position: typing.Tuple[int, int] = (0, 0)):
        self.position = position

    def get_position(self):
        return self.position

    def __repr__(self):
        return f"FakeChunk@{self.position}"


class TestBiomeMap(TestCase):
    async def test_serialize_1(self):
        buffer = WriteBuffer()
        obj = BiomeMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = BiomeMap(FakeChunk())

        await obj2.read_from_network_buffer(read_buffer)

    async def test_serialize_2(self):
        buffer = WriteBuffer()
        obj = BiomeMap(FakeChunk())
        obj.set_at_xz(0, 0, "minecraft:dessert")

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = BiomeMap(FakeChunk())

        await obj2.read_from_network_buffer(read_buffer)
        self.assertEqual(obj2.get_at_xz(0, 0), "minecraft:dessert")
        self.assertIsNone(obj2.get_at_xz(0, 4))

    async def test_migrate_v0_1(self):
        from mcpython.common.world.datafixers.versions.data_maps import BiomeMap_0_1Fixer

        BiomeMap.DATA_FIXERS[0] = BiomeMap_0_1Fixer

        buffer = WriteBuffer()
        buffer.write_uint(0)

        for i in range(16*16):
            buffer.write_uint(i % 4 + 1)

        await buffer.write_list(["a", "b", "c", "d"], lambda e: buffer.write_string(e, size_size=1))

        instance = BiomeMap(FakeChunk())
        await instance.read_from_network_buffer(ReadBuffer(buffer.get_data()))

        # This migrates all entries to the 4x4 sub-structures, so all should now be equal to "a" itself
        self.assertTrue(all(e == "a" for e in instance.biome_map.values()))


class TestLandMassMap(TestCase):
    async def test_serialize(self):
        buffer = WriteBuffer()
        obj = LandMassMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = LandMassMap(FakeChunk())

        await obj2.read_from_network_buffer(read_buffer)


class TestHeightMap(TestCase):
    async def test_serialize(self):
        buffer = WriteBuffer()
        obj = HeightMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = HeightMap(FakeChunk())
        await obj2.read_from_network_buffer(read_buffer)


class TestTemperatureMap(TestCase):
    async def test_serialize(self):
        buffer = WriteBuffer()
        obj = TemperatureMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = TemperatureMap(FakeChunk())
        await obj2.read_from_network_buffer(read_buffer)
