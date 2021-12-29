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
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer

"""
improvements for the future:
- add option to store under an special directory the data and output the binary data
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
        data = await save_file.access_file_pickle_async(file)

        if data is None:
            return
        if path not in data:
            return

        data = data[path]
        inventory.uuid = uuid.UUID(int=data["uuid"])

        buffer = ReadBuffer(data["custom data"])
        await inventory.read_from_network_buffer(buffer)

        await inventory.post_load(data["custom data"])

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
        data = await save_file.access_file_pickle_async(file) if not override else None
        if data is None:
            data = {}

        buffer = WriteBuffer()
        await inventory.write_to_network_buffer(buffer)

        inventory_data = {
            "uuid": inventory.uuid.int,
            "custom data": buffer.get_data(),
        }
        data[path] = inventory_data
        await save_file.dump_file_pickle_async(file, data)
