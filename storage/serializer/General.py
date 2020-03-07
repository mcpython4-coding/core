import storage.serializer.IDataSerializer
import globals as G


@G.registry
class General(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("level.json")
        savefile.version = data["storage version"]
        G.player.name = data["player name"]
        G.world.config = data["config"]

    @classmethod
    def save(cls, data, savefile):
        data = {
            "storage version": savefile.version,
            "player name": G.player.name,
            "config": G.world.config
        }
        savefile.dump_file_json("level.json", data)

