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
import mcpython.client.gui.ContainerRenderer
import uuid

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
    def load(
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
        data = save_file.access_file_pickle(file)

        if data is None:
            return
        if path not in data:
            return

        data = data[path]
        inventory.uuid = uuid.UUID(int=data["uuid"])
        status = inventory.load(data["custom data"])
        if not status:
            return
        [
            inventory.slots[i].load(e) if i < len(inventory.slots) else None
            for i, e in enumerate(data["slots"])
        ]
        inventory.post_load(data["custom data"])

    @classmethod
    def save(
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
        data = save_file.access_file_pickle(file) if not override else None
        if data is None:
            data = {}

        idata = {
            "uuid": inventory.uuid.int,
            "custom data": inventory.save(),
            "slots": [slot.save() for slot in inventory.slots],
        }
        data[path] = idata
        save_file.dump_file_pickle(file, data)
