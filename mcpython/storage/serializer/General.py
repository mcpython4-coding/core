"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.storage.serializer.IDataSerializer
import globals as G
import mcpython.config
import logger
import mcpython.util.getskin
import mcpython.world.player
import mcpython.ResourceLocator
import mcpython.storage.SaveFile


@G.registry
class General(mcpython.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("level.json")
        if data is None: raise mcpython.storage.serializer.IDataSerializer.MissingSaveException("level.json not found!")

        savefile.version = data["storage version"]

        playername = data["player name"]
        if playername not in G.world.players: G.world.add_player(playername)
        G.world.active_player = playername

        try:
            mcpython.util.getskin.download_skin(playername, G.build+"/skin.png")
        except ValueError:
            logger.println("[ERROR] failed to receive skin for '{}'. Falling back to default".format(playername))
            mcpython.ResourceLocator.read("assets/minecraft/textures/entity/steve.png", "pil").save(G.build+"/skin.png")
        mcpython.world.player.Player.RENDERER.reload()

        G.world.config = data["config"]
        G.eventhandler.call("seed:set")

        if data["game version"] not in mcpython.config.VERSION_ORDER:
            logger.println("future version are NOT supported. Loading may NOT work")

        for modname in data["mods"]:
            if modname not in G.modloader.mods:
                logger.println("[WARNING] mod '{}' is missing. This may break your world!".format(modname))
            elif G.modloader.mods[modname].version != tuple(data["mods"][modname]):
                try:
                    savefile.apply_mod_fixer(modname, tuple(data["mods"][modname]))
                except mcpython.storage.SaveFile.DataFixerNotFoundException:
                    if modname != "minecraft":
                        logger.println("[WARN] mod {} did not provide data-fixers for mod version change "
                                       "which occured between the sessions".format(modname))
        for modname in G.modloader.mods:
            if modname not in data["mods"]:
                savefile.apply_mod_fixer(modname, None)

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
            "game version": mcpython.config.VERSION_NAME,
            "mods": {mod.name: mod.version for mod in G.modloader.mods.values()},
            "chunks_to_generate": [(chunk.position, chunk.dimension.id) for chunk in
                                   G.worldgenerationhandler.task_handler.chunks],
            "dimensions": {dimension.id: dimension.name for dimension in G.world.dimensions.values()}
        }
        savefile.dump_file_json("level.json", data)

