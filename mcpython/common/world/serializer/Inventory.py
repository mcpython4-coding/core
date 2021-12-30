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
import uuid

import mcpython.client.gui.ContainerRenderer
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer, TableIndexedOffsetTable

"""
improvements for the future:
- make the whole serializer an network buffer and store at head an offset table
"""


@shared.registry
class Inventory(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    """
    Inventory serializer class
    todo: add part fixers
    """

    PART = NAME = "minecraft:inventory"

    @classmethod
    async def load(
        cls,
        save_file,
        inventory: mcpython.client.gui.ContainerRenderer.ContainerRenderer,
        path: str,
        file=None,
    ):
        """
        :param save_file: the save file instance
        :param inventory: The inventory to save
        :param path: the path to save under
        :param file: the file to save into
        """
        if file is None:
            file = "inventories.dat"
        data: ReadBuffer = await save_file.access_via_network_buffer(file)

        if data is None:
            return

        # Read that inventory from the data, and ignore the rest
        data: bytes = await data.read_named_offset_table_entry(path, lambda buf: buf.stream.read(), ignore_rest=True)

        buffer = ReadBuffer(data)
        await inventory.read_from_network_buffer(buffer)

    @classmethod
    async def save(
        cls,
        data,
        save_file,
        inventory: mcpython.client.gui.ContainerRenderer.ContainerRenderer,
        path: str,
        file=None,
        override=False,
    ):
        if file is None:
            file = "inventories.dat"
        data: ReadBuffer = await save_file.access_via_network_buffer(file) if not override else None

        if data is None:
            table = TableIndexedOffsetTable()
        else:
            table = await data.read_named_offset_table()

        buffer = WriteBuffer()
        await inventory.write_to_network_buffer(buffer)

        table.writeData(path, buffer.get_data())

        async def write_to(buf: WriteBuffer, d):
            buf.write_const_bytes(d)

        write = WriteBuffer()
        await write.write_named_offset_table(table, write_to)

        await save_file.dump_via_network_buffer(file, write)
