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
import io
import math
import struct
import typing
from abc import ABC
import uuid

INT = struct.Struct("!i")
LONG = struct.Struct("!q")
FLOAT = struct.Struct("!d")


class ReadBuffer:
    def __init__(self, stream: typing.Union[typing.BinaryIO, bytes]):
        self.stream = (
            stream
            if isinstance(stream, (typing.BinaryIO, io.BytesIO))
            else io.BytesIO(stream)
        )

    def read_bool(self):
        return self.stream.read(1) == b"\xFF"

    def read_struct(self, structure: struct.Struct):
        return structure.unpack(self.stream.read(structure.size))

    def read_int(self):
        return self.read_struct(INT)[0]

    def read_long(self):
        return self.read_struct(LONG)[0]

    def read_big_long(self, size_size=2):
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return int.from_bytes(self.stream.read(size), "big", signed=True)

    def read_float(self):
        return self.read_struct(FLOAT)[0]

    def read_string(self, size_size=2, encoding="utf-8"):
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return self.stream.read(size).decode(encoding)

    def read_list(self, handling: typing.Callable[[], typing.Any]):
        size = self.read_int()
        return [handling() for _ in range(size)]

    def read_bytes(self, size_size=2):
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return self.stream.read(size)

    def read_const_bytes(self, count: int):
        return self.stream.read(count)

    def read_uuid(self):
        data = self.read_long()
        return uuid.UUID(int=data)


class WriteBuffer:
    def __init__(self):
        self.data: typing.List[bytes] = []

    def get_data(self):
        return b"".join(self.data)

    def write_bool(self, state: bool):
        # todo: add a way to compress together with following single-bool fields
        self.data.append(b"\xFF" if state else b"\x00")
        return self

    def write_struct(self, structure: struct.Struct, *data):
        self.data.append(structure.pack(*data))
        return self

    def write_int(self, value: int):
        return self.write_struct(INT, value)

    def write_long(self, value: int):
        return self.write_struct(LONG, value)

    def write_big_long(self, value: int, size_size=2):
        # todo: can we optimize this calculation (one byte more is a lot bigger than we need!)?
        length = max(math.ceil(math.log(abs(value), 2 ** 8)), 0) + 1
        data = value.to_bytes(length, "big", signed=True)
        self.data.append(len(data).to_bytes(size_size, "big", signed=False))
        self.data.append(data)
        return self

    def write_float(self, value: float):
        return self.write_struct(FLOAT, value)

    def write_string(self, value: str, size_size=2, encoding="utf-8"):
        data = value.encode(encoding)
        self.data.append(len(data).to_bytes(size_size, "big", signed=False))
        self.data.append(data)
        return self

    def write_list(
        self, data: typing.List, handling: typing.Callable[[typing.Any], typing.Any]
    ):
        self.write_int(len(data))
        for e in data:
            handling(e)
        return self

    def write_bytes(self, data: bytes, size_size=2):
        self.data.append(len(data).to_bytes(size_size, "big", signed=False))
        self.data.append(data)
        return self

    def write_const_bytes(self, data: bytes):
        self.data.append(data)
        return self

    def write_uuid(self, uid: uuid.UUID):
        self.write_long(uid.int)
        return self


class IBufferSerializeAble(ABC):
    def write_to_network_buffer(self, buffer: WriteBuffer):
        pass

    def read_from_network_buffer(self, buffer: ReadBuffer):
        pass
