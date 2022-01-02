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
import importlib
import io
import math
import struct
import typing
import uuid
from abc import ABC

INT = struct.Struct("!i")
UINT = struct.Struct("!I")
LONG = struct.Struct("!q")
ULONG = struct.Struct("!Q")
FLOAT = struct.Struct("!d")
BYTE = struct.Struct("!B")


async def _to_bin(buf: "ReadBuffer"):
    return buf.stream.read()


async def _write_bin(buf: "WriteBuffer", data: bytes):
    buf.write_const_bytes(data)


class TableIndexedOffsetTable:
    def __init__(self, data: typing.Dict[str, bytes] = None, handling: typing.Callable = _to_bin):
        self.data = data if data is not None else dict()
        self.handling = handling
        self.override_data = {key: None for key in self.data.keys()}

    async def getByName(self, name: str):
        if name in self.override_data and self.override_data[name] is not None:
            return self.override_data[name]

        buffer = ReadBuffer(self.data[name])
        return await self.handling(buffer)

    def writeData(self, name: str, data: typing.Any):
        self.override_data[name] = data
        return self

    async def assemble(self, buffer: "WriteBuffer", dump_handler: typing.Callable[["WriteBuffer", typing.Any], typing.Coroutine]):
        order = list(set(self.data.keys()) | set(self.override_data.keys()))

        async def dump(d):
            b = WriteBuffer()
            r = dump_handler(b, d)

            if isinstance(r, typing.Awaitable):
                await r

            return b.get_data()

        data = [self.data[key] if self.override_data[key] is None else await dump(self.override_data[key]) for key in order]

        head = [[key, 0, len(d)] for key, d in zip(order, data)]

        c = 0
        for i, e in enumerate(head):
            e[1] = c
            c += e[2]

        await buffer.write_list(head, lambda e: buffer.write_string(e[0]).write_uint(e[1]).write_uint(e[2]))
        for e in data:
            buffer.write_const_bytes(e)


class ReadBuffer:
    def __init__(self, stream: typing.Union[typing.BinaryIO, bytes]):
        assert stream is not None, "data must be non-null"
        assert isinstance(stream, (io.BytesIO, bytes, bytearray)), f"ReadBuffer requires byte stream or bytes, got {type(stream)} ({stream})"

        self.stream = (
            stream
            if isinstance(stream, (typing.BinaryIO, io.BytesIO))
            else io.BytesIO(stream)
        )

    def read_bool(self):
        return self.stream.read(1) == b"\xFF"

    def read_bool_group(self, count: int):
        for i in range(math.ceil(count / 8)):
            d = int.from_bytes(self.read_const_bytes(1), "big", signed=False)
            s = bin(d)[2:]
            s = "0" * (8 - len(s)) + s
            s = s[: min(8, count)]
            yield from (e == "1" for e in s)
            count -= 8

    def read_struct(self, structure: struct.Struct):
        return structure.unpack(self.stream.read(structure.size))

    def read_byte(self):
        return self.read_struct(BYTE)[0]

    def read_int(self):
        return self.read_struct(INT)[0]

    def read_uint(self):
        return self.read_struct(UINT)[0]

    def read_long(self):
        return self.read_struct(LONG)[0]

    def read_ulong(self):
        return self.read_struct(ULONG)[0]

    def read_big_long(self, size_size=2):
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return int.from_bytes(self.stream.read(size), "big", signed=True)

    def read_float(self):
        return self.read_struct(FLOAT)[0]

    def read_string(self, size_size=2, encoding="utf-8") -> str:
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return self.stream.read(size).decode(encoding)

    def read_nullable_string(self, size_size=2, encoding="utf-8") -> str | None:
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        if size.bit_count() == 8 * size_size:
            return None
        return self.stream.read(size).decode(encoding)

    async def read_list(self, handling: typing.Callable[[], typing.Any]):
        size = self.read_uint()

        for _ in range(size):
            result = handling()
            if isinstance(result, typing.Awaitable):
                yield await result
            else:
                yield result

    async def collect_list(self, handling: typing.Callable[[], typing.Any]):
        return [e async for e in self.read_list(handling)]

    async def read_dict(
        self,
        key: typing.Callable[[], typing.Awaitable | typing.Hashable],
        value: typing.Callable[[], typing.Awaitable | typing.Any],
    ):
        async def maybe_async(r):
            if isinstance(r, typing.Awaitable):
                return await r

            return r

        size = self.read_uint()
        return {
            await maybe_async(key()): await maybe_async(value())
            for _ in range(size)
        }

    def read_bytes(self, size_size=2):
        size = int.from_bytes(self.stream.read(size_size), "big", signed=False)
        return self.stream.read(size)

    def read_const_bytes(self, count: int):
        return self.stream.read(count)

    def read_uuid(self):
        data = self.read_big_long()
        return uuid.UUID(int=data)

    async def read_nullable_container(self, container_instance=None) -> typing.Optional["IBufferSerializeAble"]:
        module = self.read_string()
        name = self.read_string()

        if not self.read_bool():
            return

        if container_instance is None:
            module = importlib.import_module(module)

            cls: "IBufferSerializeAble" = getattr(module, name)
            container_instance = cls.create_new()

        await container_instance.read_from_network_buffer(self)
        return container_instance

    async def read_any(self):
        tag = self.read_byte()

        match tag:
            case 0:
                return await self.collect_list(self.read_any)
            case 1:
                return tuple(await self.collect_list(self.read_any))
            case 2:
                return set(await self.collect_list(self.read_any))
            case 3:
                return await self.read_dict(self.read_any, self.read_any)
            case 4:
                return self.read_long()
            case 5:
                return self.read_float()
            case 6:
                return self.read_string()
            case 7:
                return self.read_bool()
            case 8:
                return self.read_uuid()
            case 9:
                return self.read_bytes()
            case 10:
                return None
            case 11:
                return await self.read_nullable_container()
            case 12:
                return complex(self.read_float(), self.read_float())

        raise RuntimeError(tag)

    async def read_named_offset_table(self, entry_handling: typing.Callable[["ReadBuffer"], typing.Coroutine] = _to_bin) -> TableIndexedOffsetTable:
        head = await self.collect_list(lambda: (self.read_string(), self.read_uint(), self.read_uint()))
        entries = [self.read_const_bytes(e[2]) for e in head]

        return TableIndexedOffsetTable({e[0]: d for e, d in zip(head, entries)}, entry_handling)

    async def read_named_offset_table_entry(self, key: str, entry_handling: typing.Callable[["ReadBuffer"], typing.Coroutine], ignore_rest=False):
        head = await self.collect_list(lambda: (self.read_string(), self.read_uint(), self.read_uint()))

        for e in head:
            if e[0] == key:
                info = e
                break
        else:
            raise KeyError(f"Key '{key}' not found in data")

        self.read_const_bytes(info[1])
        data = self.read_const_bytes(info[2])

        if not ignore_rest:
            self.read_const_bytes(e[1]+e[2]-info[1]-info[2])

        result = entry_handling(ReadBuffer(data))
        if isinstance(result, typing.Awaitable):
            return await result

        return result

    async def read_named_offset_table_multi_entry(self, keys: typing.Iterable[str], entry_handling: typing.Callable[["ReadBuffer"], typing.Coroutine], ignore_rest=False):
        head = await self.collect_list(lambda: (self.read_string(), self.read_uint(), self.read_uint()))
        keys = set(keys)

        for e in head:
            if e[0] in keys:
                data = self.read_const_bytes(e[2])
                keys.remove(e[0])

                result = entry_handling(ReadBuffer(data))

                if isinstance(result, typing.Awaitable):
                    yield await result
                else:
                    yield result

                if ignore_rest and not keys:
                    return
            else:
                self.read_const_bytes(e[2])

        if keys:
            raise KeyError(f"The following key(s) where not found: {', '.join(keys)}")

    async def collect_read_named_offset_table_multi_entry(self, keys: typing.Iterable[str], entry_handling: typing.Callable[["ReadBuffer"], typing.Coroutine]) -> set:
        return set([e async for e in self.read_named_offset_table_multi_entry(keys, entry_handling)])

    def read_sub_buffer_dynamic_size(self, size_size=2) -> "ReadBuffer":
        return ReadBuffer(self.read_bytes(size_size=size_size))


class WriteBuffer:
    def __init__(self):
        self.data: typing.List[bytes | typing.Callable[[], bytes]] = []

    def get_data(self) -> bytes:
        return b"".join((e if not callable(e) else e()) if not isinstance(e, WriteBuffer) else e.get_data() for e in self.data)

    def write_bool(self, state: bool):
        # todo: add a way to compress together with following single-bool fields
        self.data.append(b"\xFF" if state else b"\x00")
        return self

    def write_bool_group(self, bools: typing.List[bool]):
        for i in range(math.ceil(len(bools) / 8)):
            bits = bools[i * 8 : i * 8 + 8]
            bits += [False] * (8 - len(bits))
            self.data.append(
                int("".join("0" if not e else "1" for e in bits), base=2).to_bytes(
                    1, "big", signed=False
                )
            )

    def write_struct(self, structure: struct.Struct, *data):
        self.data.append(structure.pack(*data))
        return self

    def write_byte(self, value: int):
        return self.write_struct(BYTE, value)

    def write_int(self, value: int):
        assert isinstance(value, int), f"Value must be int, but is {type(value)} ({value})"

        return self.write_struct(INT, value)

    def write_uint(self, value: int):
        return self.write_struct(UINT, value)

    def write_long(self, value: int):
        return self.write_struct(LONG, value)

    def write_ulong(self, value: int):
        return self.write_struct(ULONG, value)

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

    def write_nullable_string(self, value: str, size_size=2, encoding="utf-8"):
        if value is None:
            self.data.append(b"\xFF"*size_size)
        else:
            data = value.encode(encoding)
            self.data.append(len(data).to_bytes(size_size, "big", signed=False))
            self.data.append(data)

        return self

    async def write_list(
        self, data: typing.Iterable, handling: typing.Callable[[typing.Any], typing.Any]
    ):
        data = tuple(data)
        self.write_uint(len(data))
        for e in data:
            result = handling(e)
            if isinstance(result, typing.Awaitable):
                await result

        return self

    async def write_dict(
        self, data: typing.Dict, key: typing.Callable, value: typing.Callable
    ):
        assert isinstance(data, dict), f"data must be a dict, not {type(data)}"

        self.write_uint(len(data))
        for k, v in data.items():
            k = key(k)

            if isinstance(k, typing.Awaitable):
                await k

            v = value(v)
            if isinstance(v, typing.Awaitable):
                await v

    def write_bytes(self, data: bytes, size_size=2):
        assert len(data) < 256 ** size_size, "data must be in bounds"

        self.data.append(len(data).to_bytes(size_size, "big", signed=False))
        self.data.append(data)
        return self

    def write_const_bytes(self, data: bytes):
        self.data.append(data)
        return self

    def write_uuid(self, uid: uuid.UUID):
        self.write_big_long(uid.int)
        return self

    async def write_nullable_container(self, container: typing.Optional["IBufferSerializeAble"]):
        cls = container.__class__

        self.write_string(cls.__module__)
        self.write_string(cls.__name__)

        if container is None:
            self.write_bool(False)
            return

        self.write_bool(True)
        await container.write_to_network_buffer(self)
        return self

    async def write_any(self, data):
        if isinstance(data, list):
            self.write_byte(0)
            await self.write_list(data, self.write_any)
        elif isinstance(data, tuple):
            self.write_byte(1)
            await self.write_list(data, self.write_any)
        elif isinstance(data, set):
            self.write_byte(2)
            await self.write_list(data, self.write_any)
        elif isinstance(data, dict):
            self.write_byte(3)
            await self.write_dict(data, self.write_any, self.write_any)
        elif isinstance(data, int):
            self.write_byte(4)
            self.write_long(data)
        elif isinstance(data, float):
            self.write_byte(5)
            self.write_float(data)
        elif isinstance(data, str):
            self.write_byte(6)
            self.write_string(data)
        elif isinstance(data, bool):
            self.write_byte(7)
            self.write_bool(data)
        elif isinstance(data, uuid.UUID):
            self.write_byte(8)
            self.write_uuid(data)
        elif isinstance(data, (bytes, bytearray)):
            self.write_byte(9)
            self.write_bytes(data)
        elif data is None:
            self.write_byte(10)
        elif isinstance(data, IBufferSerializeAble):
            self.write_byte(11)
            await self.write_nullable_container(data)
        elif isinstance(data, complex):
            self.write_byte(12)
            self.write_float(data.real)
            self.write_float(data.imag)
        else:
            raise ValueError(data)

    async def write_named_offset_table(self, handler: TableIndexedOffsetTable, dump_handler: typing.Callable[["WriteBuffer", typing.Any], typing.Coroutine] = _write_bin):
        await handler.assemble(self, dump_handler)
        return self

    def write_sub_buffer(self, buffer: "WriteBuffer"):
        self.write_const_bytes(buffer.get_data())
        return self

    def write_sub_buffer_dynamic_size(self, buffer: "WriteBuffer", size_size=2):
        self.write_bytes(buffer.get_data(), size_size=size_size)
        return self


class IBufferSerializeAble(ABC):
    @classmethod
    def create_new(cls) -> "IBufferSerializeAble":
        return cls()

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        pass

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        pass
