"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.storage.serializer.IDataSerializer
from mcpython import shared as G
import mcpython.client.gui.Inventory
import uuid

"""
improvements for the future:
- add option to store under an special directory the data and output the binary data
"""


@G.registry
class Inventory(mcpython.server.storage.serializer.IDataSerializer.IDataSerializer):
    """
    Inventory serializer class
    """

    PART = NAME = "minecraft:inventory"

    @classmethod
    def load(
        cls,
        savefile,
        inventory: mcpython.client.gui.Inventory.Inventory,
        path: str,
        file=None,
    ):
        """
        :param inventory: The inventory to save
        :param path: the path to save under
        :param file: the file to save into
        """
        if file is None:
            file = "inventories.dat"
        data = savefile.access_file_pickle(file)

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
        savefile,
        inventory: mcpython.client.gui.Inventory.Inventory,
        path: str,
        file=None,
        override=False,
    ):
        """
        :param inventory: The inventory to save
        :param path: the path to save under
        :param file: the file to save into
        """
        if file is None:
            file = "inventories.dat"
        data = savefile.access_file_pickle(file) if not override else None
        if data is None:
            data = {}

        idata = {
            "uuid": inventory.uuid.int,
            "custom data": inventory.save(),
            "slots": [slot.save() for slot in inventory.slots],
        }
        data[path] = idata
        savefile.dump_file_pickle(file, data)