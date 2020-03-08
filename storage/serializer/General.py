import storage.serializer.IDataSerializer
import globals as G
import config
import logger


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
        for modname in data["mods"]:
            if modname not in G.modloader.mods:
                logger.println("[WARNING] mod '{}' is missing. This may break your world!".format(modname))
            elif G.modloader.mods[modname].version != data["mods"][modname]:
                logger.println("[INFO] mod version did change from '{}' to '{}'. This may break your world!".format(
                    data["mods"][modname], G.modloader.mods[modname].version))

    @classmethod
    def save(cls, data, savefile):
        data = {
            "storage version": savefile.version,
            "player name": G.player.name,
            "config": G.world.config,
            "game version": config.VERSION_NAME,
            "mods": {mod.name: mod.version for mod in G.modloader.mods.values()}
        }
        savefile.dump_file_json("level.json", data)

