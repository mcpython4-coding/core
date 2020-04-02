"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import storage.serializer.IDataSerializer
import globals as G
import config
import logger
import util.getskin
import world.player
import ResourceLocator


@G.registry
class General(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("level.json")
        if data is None: raise storage.serializer.IDataSerializer.InvalidSaveException("level.json not found!")
        savefile.version = data["storage version"]
        playername = data["player name"]
        if playername not in G.world.players: G.world.add_player(playername)
        G.world.active_player = playername
        try:
            util.getskin.download_skin(playername, G.local+"/build/skin.png")
        except ValueError:
            logger.println("[ERROR] failed to receive skin for '{}'. Falling back to default".format(playername))
            ResourceLocator.read("assets/minecraft/textures/entity/steve.png", "pil").save(G.local + "/build/skin.png")
        world.player.Player.RENDERER.reload()
        G.world.config = data["config"]
        G.eventhandler.call("seed:set")
        if data["game version"] not in config.VERSION_ORDER:
            raise storage.serializer.IDataSerializer.InvalidSaveException("future version are NOT supported")
        for modname in data["mods"]:
            if modname not in G.modloader.mods:
                logger.println("[WARNING] mod '{}' is missing. This may break your world!".format(modname))
            elif G.modloader.mods[modname].version != tuple(data["mods"][modname]):
                logger.println("[INFO] mod version did change from '{}' to '{}'. This may break your world!".format(
                    data["mods"][modname], tuple(G.modloader.mods[modname].version)))
        [G.worldgenerationhandler.add_chunk_to_generation_list(e[0], dimension=e[1]) for e in data["chunks_to_generate"]]
        for dimension in G.world.dimensions.values():
            if str(dimension.id) in data["dimensions"]:
                if data["dimensions"][str(dimension.id)] != dimension.name:
                    logger.println("[WARN] dimension name changed for dim {} from '{}' to '{}'".format(
                        dimension.id, data["dimensions"][str(dimension.id)], dimension.name))
                del data["dimensions"][str(dimension.id)]
            else:
                logger.println("[WARN] dimension {} not arrival in save".format(dimension.id))
        for dim in data["dimensions"]:
            logger.println("[WARN] dimension {} named '{}' is arrival in save but not registered in game".format(
                dim, data["dimensions"][dim]))

    @classmethod
    def save(cls, data, savefile):
        data = {
            "storage version": savefile.version,
            "player name": G.world.get_active_player().name,
            "config": G.world.config,
            "game version": config.VERSION_NAME,
            "mods": {mod.name: mod.version for mod in G.modloader.mods.values()},
            "chunks_to_generate": [(chunk.position, chunk.dimension.id) for chunk in G.worldgenerationhandler.
                tasks_to_generate + G.worldgenerationhandler.runtimegenerationcache[0]],
            "dimensions": {dimension.id: dimension.name for dimension in G.world.dimensions.values()}
        }
        savefile.dump_file_json("level.json", data)

