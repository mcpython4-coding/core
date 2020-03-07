import storage.serializer.IDataSerializer
import globals as G
import config


@G.registry
class General(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("level.json")
        savefile.version = data["storage version"]
        G.player.name = data["player name"]
        G.world.config = data["config"]
        if data["game version"] not in config.VERSION_ORDER:
            raise storage.serializer.IDataSerializer.InvalidSaveException("future version are NOT supported")

    @classmethod
    def save(cls, data, savefile):
        data = {
            "storage version": savefile.version,
            "player name": G.player.name,
            "config": G.world.config,
            "game version": config.VERSION_NAME
        }
        savefile.dump_file_json("level.json", data)

