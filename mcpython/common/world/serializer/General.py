"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.ResourceLoader
import mcpython.common.config
import mcpython.common.world.SaveFile
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer
import mcpython.util.getskin
import mcpython.common.entity.PlayerEntity
import mcpython.server.worldgen.noise.NoiseManager


class WorldConfigFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Class representing an fix for the config-entry
    """

    TARGET_SERIALIZER_NAME = "minecraft:general_config"

    @classmethod
    def fix(cls, save_file, data: dict) -> dict:
        raise NotImplementedError()


class WorldGeneralFixer(mcpython.common.world.datafixers.IDataFixer.IPartFixer):
    """
    Class representing an fix for the config-entry
    """

    TARGET_SERIALIZER_NAME = "minecraft:general"

    @classmethod
    def fix(cls, save_file, data: dict) -> dict:
        raise NotImplementedError()


@shared.registry
class General(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    def apply_part_fixer(cls, save_file, fixer):
        # when it is another version, loading MAY fail
        if save_file.version != mcpython.common.world.SaveFile.LATEST_VERSION:
            return

        if issubclass(fixer, WorldConfigFixer):
            data = save_file.access_file_json("level.json")
            data["config"] = fixer.fix(save_file, data["config"])
            save_file.write_file_json("level.json", data)

        elif issubclass(fixer, WorldGeneralFixer):
            data = save_file.access_file_json("level.json")
            data = fixer.fix(save_file, data)
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
            mcpython.util.getskin.download_skin(player_name, shared.build + "/skin.png")
        except ValueError:
            logger.println(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    player_name
                )
            )
            mcpython.ResourceLoader.read_image(
                "assets/minecraft/textures/entity/steve.png"
            ).save(shared.build + "/skin.png")

        try:
            mcpython.common.entity.PlayerEntity.PlayerEntity.RENDERER.reload()
        except AttributeError:
            pass

        shared.world.config = data["config"]
        shared.event_handler.call("seed:set")

        if type(data["game version"]) != int:
            logger.println("Old version name format found!")
            logger.println("it was last loaded in '{}'".format(data["game version"]))
            data["game version"] = -1

        for modname in data["mods"]:
            if modname not in shared.mod_loader.mods:
                logger.println(
                    "[WARNING] mod '{}' is missing. This may break your world!".format(
                        modname
                    )
                )
            elif shared.mod_loader.mods[modname].version != tuple(
                data["mods"][modname]
            ):
                try:
                    save_file.apply_mod_fixer(modname, tuple(data["mods"][modname]))
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    if modname != "minecraft":
                        logger.println(
                            "[WARN] mod {} did not provide data-fixers for mod version change "
                            "which occur between the sessions (from {} to {})".format(
                                modname,
                                tuple(data["mods"][modname]),
                                shared.mod_loader.mods[modname].version,
                            )
                        )

        # apply data fixers for creating mod data
        for modname in shared.mod_loader.mods:
            if modname not in data["mods"]:
                try:
                    save_file.apply_mod_fixer(modname, None)
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    pass

        # the chunks scheduled for generation
        [
            shared.world_generation_handler.add_chunk_to_generation_list(
                e[0], dimension=e[1]
            )
            for e in data["chunks_to_generate"]
        ]

        for dimension in shared.world.dimensions.values():
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
            shared.world.join_dimension(data["active_dimension"])

        wd = data["world_gen_info"]
        mcpython.server.worldgen.noise.NoiseManager.manager.default_implementation = wd[
            "noise_implementation"
        ]
        shared.world_generation_handler.deserialize_chunk_generator_info(
            wd["chunk_generators"]
        )
        mcpython.server.worldgen.noise.NoiseManager.manager.deserialize_seed_map(
            wd["seeds"]
        )
        mcpython.server.worldgen.noise.NoiseManager.manager.set_noise_implementation()

    @classmethod
    def save(cls, data, save_file):
        data = {
            "storage version": save_file.version,  # the storage version stored in
            "player name": shared.world.get_active_player().name,  # the name of the player the world played in
            "config": shared.world.config,  # the world config
            "game version": mcpython.common.config.VERSION_ID,
            "mods": {mod.name: mod.version for mod in shared.mod_loader.mods.values()},
            "chunks_to_generate": [
                (chunk.get_position(), chunk.get_dimension().get_id())
                for chunk in shared.world_generation_handler.task_handler.chunks
            ],
            "dimensions": {
                dimension.get_id(): dimension.get_name()
                for dimension in shared.world.dimensions.values()
            },
            "active_dimension": shared.world.get_active_player().dimension.get_id(),
            "world_gen_info": {
                "noise_implementation": mcpython.server.worldgen.noise.NoiseManager.manager.default_implementation,
                "chunk_generators": shared.world_generation_handler.serialize_chunk_generator_info(),
                "seeds": mcpython.server.worldgen.noise.NoiseManager.manager.serialize_seed_map().update(
                    {
                        "minecraft:noise_implementation": mcpython.server.worldgen.noise.NoiseManager.manager.default_implementation
                    }
                ),
            },
        }
        save_file.dump_file_json("level.json", data)
