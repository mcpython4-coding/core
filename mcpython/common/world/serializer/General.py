"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.ResourceLoader
import mcpython.common.config
import mcpython.common.world.SaveFile
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer
import mcpython.util.getskin
import mcpython.common.world.player


class WorldConfigFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Class representing an fix for the config-entry
    """

    TARGET_SERIALIZER_NAME = "minecraft:general"

    @classmethod
    def fix(cls, save_file, data: dict) -> dict:
        raise NotImplementedError()


@G.registry
class General(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def apply_part_fixer(cls, save_file, fixer):
        # when it is another version, loading MAY fail
        if save_file.version != mcpython.common.world.SaveFile.LATEST_VERSION:
            return

        data = save_file.access_file_json("level.json")
        data["config"] = fixer.fix(save_file, data["config"])
        save_file.write_file_json("level.json", data)

    @classmethod
    def load(cls, save_file):
        data = save_file.access_file_json("level.json")
        if data is None:
            raise mcpython.common.world.serializer.IDataSerializer.MissingSaveException(
                "level.json not found!"
            )

        save_file.version = data["storage version"]

        # when it is another version, loading MAY fail
        if save_file.version != mcpython.common.world.SaveFile.LATEST_VERSION:
            return

        player_name = data["player name"]

        try:
            mcpython.util.getskin.download_skin(player_name, G.build + "/skin.png")
        except ValueError:
            logger.println(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    player_name
                )
            )
            mcpython.ResourceLoader.read_image(
                "assets/minecraft/textures/entity/steve.png"
            ).get_save_data(G.build + "/skin.png")
        mcpython.common.world.player.Player.RENDERER.reload()

        G.world.config = data["config"]
        G.event_handler.call("seed:set")

        if data["game version"] not in mcpython.common.config.VERSION_ORDER:
            logger.println(
                "Future version are NOT supported. Loading may NOT work (but we try to)"
            )
            logger.println(
                "Whatever happens to you saves now, we CAN NOT give you help. For your information, "
            )
            logger.println("it was last loaded in '{}'".format(data["game version"]))

        for modname in data["mods"]:
            if modname not in G.mod_loader.mods:
                logger.println(
                    "[WARNING] mod '{}' is missing. This may break your world!".format(
                        modname
                    )
                )
            elif G.mod_loader.mods[modname].version != tuple(data["mods"][modname]):
                try:
                    save_file.apply_mod_fixer(modname, tuple(data["mods"][modname]))
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    if modname != "minecraft":
                        logger.println(
                            "[WARN] mod {} did not provide data-fixers for mod version change "
                            "which occur between the sessions (from {} to {})".format(
                                modname,
                                tuple(data["mods"][modname]),
                                G.mod_loader.mods[modname].version,
                            )
                        )

        # apply data fixers for creating mod data
        for modname in G.mod_loader.mods:
            if modname not in data["mods"]:
                try:
                    save_file.apply_mod_fixer(modname, None)
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    pass

        # the chunks scheduled for generation
        [
            G.world_generation_handler.add_chunk_to_generation_list(
                e[0], dimension=e[1]
            )
            for e in data["chunks_to_generate"]
        ]

        for dimension in G.world.dimensions.values():
            if str(dimension.id) in data["dimensions"]:
                if data["dimensions"][str(dimension.id)] != dimension.name:
                    logger.println(
                        "[WARN] dimension name changed for dim {} from '{}' to '{}'".format(
                            dimension.id,
                            data["dimensions"][str(dimension.id)],
                            dimension.name,
                        )
                    )
                del data["dimensions"][str(dimension.id)]
            else:
                logger.println(
                    "[WARN] dimension {} not arrival in save".format(dimension.id)
                )
        for dim in data["dimensions"]:
            logger.println(
                "[WARN] dimension {} named '{}' is arrival in save but not registered in game".format(
                    dim, data["dimensions"][dim]
                )
            )

        if "active_dimension" in data:
            G.world.join_dimension(data["active_dimension"])

    @classmethod
    def save(cls, data, save_file):
        data = {
            "storage version": save_file.version,  # the storage version stored in
            "player name": G.world.get_active_player().name,  # the name of the player the world played in
            "config": G.world.config,  # the world config
            "game version": mcpython.common.config.VERSION_NAME,
            "mods": {mod.name: mod.version for mod in G.mod_loader.mods.values()},
            "chunks_to_generate": [
                (chunk.position, chunk.dimension.id)
                for chunk in G.world_generation_handler.task_handler.chunks
            ],
            "dimensions": {
                dimension.id: dimension.name
                for dimension in G.world.dimensions.values()
            },
            "active_dimension": G.world.get_active_player().dimension.id,
        }
        save_file.dump_file_json("level.json", data)
