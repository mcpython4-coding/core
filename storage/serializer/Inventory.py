"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import storage.serializer.IDataSerializer
import globals as G
import gui.Inventory
import uuid

"""
improvements for the future:
- add option to store under an special directory the data and output the binary data
"""


@G.registry
class Inventory(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:inventory"

    @classmethod
    def load(cls, savefile, inventory: gui.Inventory.Inventory, path: str, file=None):
        if file is None: file = "inventories.dat"
        data = savefile.access_file_pickle(file)
        if data is None: return
        if "version" in data and data["version"] != savefile.version:
            savefile.upgrade("minecraft:inventory_file", version=data["version"], path=path, file=file)
            data = savefile.access_file_pickle(file)
        if path not in data: return
        data = data[path]
        inventory.uuid = uuid.UUID(int=data["uuid"])
        status = inventory.load(data["custom data"])
        if not status: return
        [inventory.slots[i].load(e) if i < len(inventory.slots) else None for i, e in enumerate(data["slots"])]

    @classmethod
    def save(cls, data, savefile, inventory: gui.Inventory.Inventory, path: str, file=None, override=False):
        if file is None: file = "inventories.dat"
        data = savefile.access_file_pickle(file) if not override else None
        if data is None: data = {"version": savefile.version}
        idata = {"uuid": inventory.uuid.int,
                 "custom data": inventory.save(),
                 "slots": [slot.save() for slot in inventory.slots]}
        data[path] = idata
        savefile.dump_file_pickle(file, data)

