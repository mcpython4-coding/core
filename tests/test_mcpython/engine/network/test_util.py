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
import asyncio
import random
import string
import typing
import unittest
import uuid
from unittest import TestCase

# These is a list of tests that we can execute on buffers, used for the multi test
from mcpython.engine.network.util import IBufferSerializeAble

MULTI_TEST_POOL: typing.List[
    typing.Tuple[typing.Callable, typing.Callable, typing.Callable]
] = [
    (
        lambda: bool(random.randint(0, 1)),
        lambda buffer, v: buffer.write_bool(v),
        lambda buffer, v: buffer.read_bool() == v,
    ),
    (
        lambda: random.randint(-100000, 100000000),
        lambda buffer, v: buffer.write_int(v),
        lambda buffer, v: buffer.read_int() == v,
    ),
    (
        lambda: random.randint(-100000, 100000000),
        lambda buffer, v: buffer.write_long(v),
        lambda buffer, v: buffer.read_long() == v,
    ),
    (
        lambda: (random.randint(-100000, 100000000), random.randint(2, 5)),
        lambda buffer, v: buffer.write_big_long(v[0], v[1]),
        lambda buffer, v: buffer.read_big_long(v[1]) == v[0],
    ),
    (
        lambda: random.randint(-100000, 100000) / random.randint(1, 1000000),
        lambda buffer, v: buffer.write_float(v),
        lambda buffer, v: buffer.read_float() == v,
    ),
    (
        lambda: "".join(
            random.choice(string.printable) for _ in range(random.randint(10, 1000))
        ),
        lambda buffer, v: buffer.write_string(v),
        lambda buffer, v: buffer.read_string() == v,
    ),
    (
        lambda: "".join(
            random.choice(string.printable) for _ in range(random.randint(10, 1000))
        )
        if random.random() > 0.5
        else None,
        lambda buffer, v: buffer.write_nullable_string(v),
        lambda buffer, v: buffer.read_nullable_string() == v,
    ),
    (
        lambda: uuid.uuid4(),
        lambda buffer, v: buffer.write_uuid(v),
        lambda buffer, v: buffer.read_uuid() == v,
    ),
    (
        lambda: [bool(random.randint(0, 1)) for _ in range(random.randint(10, 50))],
        lambda buffer, v: buffer.write_bool_group(v),
        lambda buffer, v: list(buffer.read_bool_group(len(v))) == v,
    ),
    (
        lambda: random.randint(0, 255),
        lambda buffer, v: buffer.write_byte(v),
        lambda buffer, v: buffer.read_byte() == v,
    ),
]


class TestBuffer(TestCase):
    def test_empty(self):
        from mcpython.engine.network.util import WriteBuffer

        buffer = WriteBuffer()
        self.assertEqual(buffer.get_data(), bytes())

    def test_bool_false(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        write = WriteBuffer()

        write.write_bool(False)

        read = ReadBuffer(write.get_data())

        self.assertFalse(read.read_bool())

    def test_bool_true(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        write = WriteBuffer()

        write.write_bool(True)

        read = ReadBuffer(write.get_data())

        self.assertTrue(read.read_bool())

    # todo: some struct tests

    def test_bool_group(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(10):
            group = [bool(random.randint(0, 1)) for _ in range(4, 40)]

            write = WriteBuffer()
            write.write_bool_group(group)

            read = ReadBuffer(write.get_data())

            self.assertEqual(list(read.read_bool_group(len(group))), group)

    def test_byte(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = random.randint(0, 255)

            write = WriteBuffer()

            write.write_byte(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_byte(), v)

    def test_bytes_1(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = bytes([random.randint(0, 255) for _ in range(random.randint(10, 50))])

            write = WriteBuffer()

            write.write_bytes(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_bytes(), v)

    def test_bytes_2(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = bytes([random.randint(0, 255) for _ in range(random.randint(10, 200))])
            size_size = random.randint(1, 5)

            write = WriteBuffer()

            write.write_bytes(v, size_size=size_size)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_bytes(size_size=size_size), v)

    def test_int(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)

            write = WriteBuffer()

            write.write_int(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_int(), v)

    def test_long(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)

            write = WriteBuffer()

            write.write_long(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_long(), v)

    def test_big_long(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)
            size = random.randint(2, 5)

            write = WriteBuffer()

            write.write_big_long(v, size)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_big_long(size), v)

    def test_float(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000) / random.randint(1, 1000000)

            write = WriteBuffer()

            write.write_float(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_float(), v)

    def test_string(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            text = "".join(
                random.choice(string.printable) for _ in range(random.randint(10, 1000))
            )

            write = WriteBuffer()

            write.write_string(text)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_string(), text)

    def test_uuid(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(20):
            d = uuid.uuid4()

            write = WriteBuffer()

            write.write_uuid(d)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_uuid(), d)

    # todo: add a list test and bytes tests

    def test_multi(self):
        # tests out chains of data
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(10):
            count = random.randint(4, 20)
            entries = [random.choice(MULTI_TEST_POOL) for _ in range(count)]
            data = [e[0]() for e in entries]

            write = WriteBuffer()

            for i, e in enumerate(entries):
                e[1](write, data[i])

            read = ReadBuffer(write.get_data())

            for i, e in enumerate(entries):
                self.assertTrue(e[2](read, data[i]), e)

    async def test_multi_any(self):
        # tests out chains of data
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        for _ in range(10):
            count = random.randint(4, 20)
            entries = [random.choice(MULTI_TEST_POOL) for _ in range(count)]
            data = [e[0]() for e in entries]

            write = WriteBuffer()

            for i, e in enumerate(entries):
                await write.write_any(data[i])

            read = ReadBuffer(write.get_data())

            for i, e in enumerate(entries):
                self.assertEqual(data[i], await read.read_any())

    async def test_named_offset_table_1(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (0, 8, 4.9))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        read = ReadBuffer(buffer.get_data())

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        table2 = await read.read_named_offset_table(read_entry)

        self.assertEqual(await table2.getByName("test"), (0, 8, 4.5))
        self.assertEqual(await table2.getByName("test2"), (0, 8, 4.9))

    async def test_named_offset_table_2(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (0, 8, 4.9))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        read = ReadBuffer(buffer.get_data())

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        table2 = await read.read_named_offset_table(read_entry)
        table2.writeData("test3", (90, 0, -7.9))

        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table2,
            lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2]),
        )

        read = ReadBuffer(buffer.get_data())
        table2 = await read.read_named_offset_table(read_entry)

        self.assertEqual(await table2.getByName("test"), (0, 8, 4.5))
        self.assertEqual(await table2.getByName("test2"), (0, 8, 4.9))
        self.assertEqual(await table2.getByName("test3"), (90, 0, -7.9))

    async def test_named_offset_table_offset_1(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (0, 8, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        read = ReadBuffer(buffer.get_data())

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        self.assertEqual(
            await read.read_named_offset_table_entry("test", read_entry), (0, 8, 4.5)
        )

    async def test_named_offset_table_offset_2(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (-8, 12, 4.5))
        table.writeData("test3", (0, 9, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        read = ReadBuffer(buffer.get_data())

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        self.assertEqual(
            await read.read_named_offset_table_entry("test2", read_entry), (-8, 12, 4.5)
        )

    async def test_named_offset_table_offset_3(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (-8, 12, 4.5))
        table.writeData("test3", (0, 9, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        read = ReadBuffer(buffer.get_data())

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        await self.assertRaisesAsync(
            KeyError, read.read_named_offset_table_entry("invalid", read_entry)
        )

    async def assertRaisesAsync(self, expected_exception, coroutine):
        try:
            await coroutine
        except expected_exception:
            return
        self.assertTrue(False)

    async def test_named_offset_multi_table_offset_1(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (-8, 12, 4.5))
        table.writeData("test3", (0, 9, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        data = buffer.get_data()
        read = ReadBuffer(data)

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        self.assertEqual(
            await read.collect_read_named_offset_table_multi_entry(
                ["test2", "test"], read_entry
            ),
            {(-8, 12, 4.5), (0, 8, 4.5)},
        )

    async def test_named_offset_multi_table_offset_2(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (-8, 12, 4.5))
        table.writeData("test3", (0, 9, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        data = buffer.get_data()
        read = ReadBuffer(data)

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        await self.assertRaisesAsync(
            KeyError,
            read.collect_read_named_offset_table_multi_entry(
                ["test2", "invalid"], read_entry
            ),
        )

    async def test_named_offset_table_write(self):
        from mcpython.engine.network.util import (
            ReadBuffer,
            TableIndexedOffsetTable,
            WriteBuffer,
        )

        table = TableIndexedOffsetTable()
        table.writeData("test", (0, 8, 4.5))
        table.writeData("test2", (-8, 12, 4.5))
        table.writeData("test3", (0, 9, 4.5))
        buffer = WriteBuffer()
        await buffer.write_named_offset_table(
            table, lambda buf, e: buf.write_int(e[0]).write_uint(e[1]).write_float(e[2])
        )

        data = buffer.get_data()
        read = ReadBuffer(data)

        async def read_entry(buf):
            return buf.read_int(), buf.read_uint(), buf.read_float()

        table: TableIndexedOffsetTable = await read.read_named_offset_table(read_entry)
        table.writeData("test", (0, 2, -6.8))
        self.assertEqual(await table.getByName("test"), (0, 2, -6.8))

    async def test_skipable_list_1(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_skipable_list(list(range(20)), WriteBuffer.write_int)
        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_skipable_list(lambda b: b.read_int())

        self.assertEqual(await data.to_list(), list(range(20)))

    async def test_skipable_list_2(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_skipable_list(list(range(20)), WriteBuffer.write_int)
        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_skipable_list(lambda b: b.read_int())

        self.assertEqual(await data.to_partial_list(10), list(range(10)))
        data.skip()
        self.assertEqual(await data.to_list(), list(range(11, 20)))

    async def test_skipable_list_3(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_skipable_list(list(range(20)), WriteBuffer.write_int)
        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_skipable_list(ReadBuffer.read_int)

        self.assertEqual(await data.to_partial_list(10), list(range(10)))
        data.skip(4)
        self.assertEqual(await data.to_list(), list(range(14, 20)))

    async def test_equal_list_1(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_equal_spaced_list(list(range(20)), WriteBuffer.write_int)
        buffer.write_int(1025)

        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_equal_spaced_list(ReadBuffer.read_int)

        self.assertEqual(await data.to_partial_list(10), list(range(10)))
        data.skip(4)
        self.assertEqual(await data.to_list(), list(range(14, 20)))

    async def test_equal_list_2(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_equal_spaced_list(list(range(20)), WriteBuffer.write_int)
        buffer.write_int(1025)

        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_single_element_from_equal_spaced_list(
            3, ReadBuffer.read_int
        )

        self.assertEqual(data, 3)

    async def test_equal_list_3(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_equal_spaced_list(list(range(20)), WriteBuffer.write_int)
        buffer.write_int(1025)

        read_buffer = ReadBuffer(buffer.get_data())
        data = await read_buffer.read_multi_element_from_equal_spaced_list(
            [3, 7, 5], ReadBuffer.read_int
        )

        self.assertEqual(data, [3, 7, 5])


class Simple(IBufferSerializeAble):
    def __init__(self):
        self.valid = False

    async def read_from_network_buffer(self, buffer):
        self.valid = buffer.read_int() == 42

    async def write_to_network_buffer(self, buffer):
        buffer.write_int(42)


class TestContainerSerializer(unittest.TestCase):
    async def test_basic(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        obj = Simple()
        await buffer.write_nullable_container(obj)

        read = ReadBuffer(buffer.get_data())
        obj: Simple = await read.read_nullable_container()
        self.assertIsNotNone(obj)
        self.assertTrue(obj.valid)

    async def test_basic_null(self):
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        buffer = WriteBuffer()
        await buffer.write_nullable_container(None)

        read = ReadBuffer(buffer.get_data())
        self.assertIsNone(await read.read_nullable_container())
