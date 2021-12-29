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
    async def test_serialize(self):
        buffer = WriteBuffer()
        obj = BiomeMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = BiomeMap(FakeChunk())

        await obj2.read_from_network_buffer(read_buffer)


class TestLandMassMap(TestCase):
    async def test_serialize(self):
        buffer = WriteBuffer()
        obj = LandMassMap(FakeChunk())

        await obj.write_to_network_buffer(buffer)

        read_buffer = ReadBuffer(buffer.get_data())
        obj2 = LandMassMap(FakeChunk())

        await obj2.read_from_network_buffer(read_buffer)
        # self.assertEqual(obj.land_mass_map, obj2.land_mass_map)
