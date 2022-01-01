from unittest import TestCase

from mcpython import shared
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer

shared.IS_TEST_ENV = True

from mcpython.server.worldgen.map.BiomeMap import BiomeMap
from mcpython.server.worldgen.map.FeatureMap import FeatureMap
from mcpython.server.worldgen.map.HeightMap import HeightMap
from mcpython.server.worldgen.map.LandMassMap import LandMassMap
from mcpython.server.worldgen.map.TemperatureMap import TemperatureMap


class FakeChunk:
    def get_position(self):
        return 0, 0


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
        self.assertIsNone(obj2.get_at_xz(0, 1))


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
