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
from unittest import TestCase
import random
import string


# These is a list of tests that we can execute on buffers, used for the multi test
MULTI_TEST_POOL: typing.List[typing.Tuple[typing.Callable, typing.Callable, typing.Callable]] = [
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
        lambda: "".join(random.choice(string.printable) for _ in range(random.randint(10, 1000))),
        lambda buffer, v: buffer.write_string(v),
        lambda buffer, v: buffer.read_string() == v,
    )
]


class TestBuffer(TestCase):
    def test_module_import(self):
        import mcpython.engine.network.util

    def test_empty(self):
        from mcpython.engine.network.util import WriteBuffer

        buffer = WriteBuffer()
        self.assertEqual(buffer.get_data(), bytes())

    def test_bool_false(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        write = WriteBuffer()

        write.write_bool(False)

        read = ReadBuffer(write.get_data())

        self.assertFalse(read.read_bool())

    def test_bool_true(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        write = WriteBuffer()

        write.write_bool(True)

        read = ReadBuffer(write.get_data())

        self.assertTrue(read.read_bool())

    # todo: some struct tests

    def test_int(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)

            write = WriteBuffer()

            write.write_int(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_int(), v)

    def test_long(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)

            write = WriteBuffer()

            write.write_long(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_long(), v)

    def test_big_long(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000)
            size = random.randint(2, 5)

            write = WriteBuffer()

            write.write_big_long(v, size)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_big_long(size), v)

    def test_float(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(20):
            v = random.randint(-100000, 100000) / random.randint(1, 1000000)

            write = WriteBuffer()

            write.write_float(v)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_float(), v)

    def test_string(self):
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(20):
            text = "".join(random.choice(string.printable) for _ in range(random.randint(10, 1000)))

            write = WriteBuffer()

            write.write_string(text)

            read = ReadBuffer(write.get_data())

            self.assertEqual(read.read_string(), text)

    # todo: add a list test and bytes tests

    def test_multi(self):
        # tests out chains of data
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        for _ in range(10):
            count = random.randint(4, 20)
            entries = [random.choice(MULTI_TEST_POOL) for _ in range(count)]
            data = [e[0]() for e in entries]

            write = WriteBuffer()

            for i, e in enumerate(entries):
                e[1](write, data[i])

            read = ReadBuffer(write.get_data())

            for i, e in enumerate(entries):
                self.assertTrue(e[2](read, data[i]))
