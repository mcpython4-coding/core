import storage.serializer.IDataSerializer
import globals as G
import world.GameRule


@G.registry
class GameRule(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:gamerule"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("gamerules.json")
        if data is None: pass
        for name in data:
            G.world.gamerulehandler.table[name].status.load(data[name])

    @classmethod
    def save(cls, data, savefile):
        data = {gamerule.NAME: gamerule.status.save() for gamerule in G.world.gamerulehandler.table.values()}
        savefile.dump_file_json("gamerules.json", data)

