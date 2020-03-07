import storage.serializer.IDataSerializer
import globals as G
import gui.Inventory
import uuid


@G.registry
class Inventory(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:inventory"

    @classmethod
    def load(cls, savefile, inventory: gui.Inventory.Inventory, path: str):
        data = savefile.access_file_pickle("inventories.dat")
        if data is None: return
        if "version" in data and data["version"] != savefile.version:
            savefile.upgrade("inventory_file")
        if path not in data: return
        data = data[path]
        inventory.uuid = uuid.UUID(int=data["uuid"])
        status = inventory.load(data["custom data"])
        if not status: return
        [inventory.slots[i].load(e) for i, e in enumerate(data["slots"])]

    @classmethod
    def save(cls, data, savefile, inventory: gui.Inventory.Inventory, path: str):
        data = savefile.access_file_pickle("inventories.dat")
        if data is None: data = {"version": savefile.version}
        idata = {"uuid": inventory.uuid.int,
                 "custom data": inventory.save(),
                 "slots": [slot.save() for slot in inventory.slots]}
        data[path] = idata
        savefile.dump_file_pickle("inventories.dat", data)

