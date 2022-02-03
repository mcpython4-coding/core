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
from mcpython import shared

shared.IS_CLIENT = False

import mcpython.common.block.BlockManager
from mcpython.common.factory.BlockFactory import BlockFactory
from tests.util import TestCase

test_block = BlockFactory().set_name("test:block").finish()


class FakeDim:
    def get_world_height_range(self):
        return 0, 255

    def get_name(self):
        return "overworld"

    def get_block(self, position):
        pass


class TestChunk(TestCase):
    def test_module_import(self):
        import mcpython.common.world.Chunk

    def test_entity_iterator(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk(None, (0, 0))
        e = "test:entity"
        instance.entities.add(e)
        self.assertEqual(list(instance.entity_iterator()), [e])

    def test_mark_dirty(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk(None, (0, 0))

        self.assertFalse(instance.dirty)

        instance.mark_dirty()

        self.assertTrue(instance.dirty)

    def test_get_dimension(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk("test:dimension", (0, 0))
        self.assertEqual(instance.get_dimension(), "test:dimension")

    def test_get_position(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk(None, (10, 20))
        self.assertEqual(instance.get_position(), (10, 20))

    def test_exposed_faces(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk(None, (0, 0))
        self.assertEqual(instance.exposed_faces((0, 0, 0)), instance.ALL_FACES_EXPOSED)

    def test_is_position_blocked(self):
        from mcpython.common.world.Chunk import Chunk

        instance = Chunk(None, (0, 0))
        self.assertFalse(instance.is_position_blocked((0, 0, 0)))

        instance._world[(0, 0, 0)] = "test"
        self.assertTrue(instance.is_position_blocked((0, 0, 0)))

    async def test_add_block_by_str(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        b = await instance.add_block((0, 0, 0), "test:block")
        self.assertEqual(instance.get_block((0, 0, 0)), b)

        self.assertTrue(instance.dirty)

    async def test_add_block_by_instance(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        b = await instance.add_block((0, 0, 0), test_block)
        self.assertEqual(instance.get_block((0, 0, 0)), b)

    async def test_add_block_out_of_bounds(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, -10, 0), test_block)
        self.assertEqual(instance.get_block((0, -10, 0)), None)

    # todo: why does this fail on CI?
    # def test_add_block_non_integer(self):
    #     from mcpython.common.world.Chunk import Chunk
    #
    #     dim = FakeDim()
    #
    #     instance = Chunk(dim, (0, 0))
    #     self.assertRaises(
    #         ValueError, lambda: instance.add_block((0, 0, 0.10), test_block)
    #     )

    async def test_add_block_air_via_None(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, 0, 0), test_block)
        await instance.add_block((0, 0, 0), None)
        self.assertEqual(instance.get_block((0, 0, 0)), None)

    async def test_add_block_air_via_name(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, 0, 0), test_block)
        await instance.add_block((0, 0, 0), "air")
        self.assertEqual(instance.get_block((0, 0, 0)), None)

    async def test_add_block_air_via_namespaced_name(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, 0, 0), test_block)
        await instance.add_block((0, 0, 0), "minecraft:air")
        self.assertEqual(instance.get_block((0, 0, 0)), None)

    async def test_add_block_invalid_name(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, 0, 0), test_block)
        await instance.add_block((0, 0, 0), "test:invalid")
        self.assertEqual(instance.get_block((0, 0, 0)), None)

    async def test_remove_block_by_position(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.add_block((0, 0, 0), "test:block")
        await instance.remove_block((0, 0, 0))
        self.assertEqual(instance.get_block((0, 0, 0)), None)

        self.assertTrue(instance.dirty)

    # Test for issue 1001
    async def test_remove_block_by_instance(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        b = await instance.add_block((0, 0, 0), "test:block")
        await instance.remove_block(b)
        self.assertEqual(instance.get_block((0, 0, 0)), None)

    async def test_safe_removal_when_not_in_world(self):
        from mcpython.common.world.Chunk import Chunk

        dim = FakeDim()

        instance = Chunk(dim, (0, 0))
        await instance.remove_block((0, 0, 0))
