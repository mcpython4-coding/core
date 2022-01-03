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
import mcpython.common.config
import mcpython.common.entity.PlayerEntity
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.SaveFile
import mcpython.common.world.serializer.IDataSerializer
import mcpython.engine.ResourceLoader
import mcpython.server.worldgen.noise.NoiseManager
import mcpython.util.getskin
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


@shared.registry
class General(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:general"

    @classmethod
    async def load(cls, save_file):
        read_buffer: ReadBuffer = await save_file.access_via_network_buffer("level.dat")
        if read_buffer is None:
            raise mcpython.common.world.serializer.IDataSerializer.MissingSaveException(
                "level.json not found!"
            )

        save_file.version = read_buffer.read_ulong()

        # when it is another version, loading MAY fail
        if save_file.version != mcpython.common.world.SaveFile.LATEST_VERSION:
            return

        version_id = read_buffer.read_ulong()
        player_name = read_buffer.read_string()

        mods = await read_buffer.read_dict(
            read_buffer.read_string, read_buffer.read_any
        )
        chunks_to_generate = await read_buffer.collect_list(
            lambda: (
                read_buffer.read_int(),
                read_buffer.read_long(),
                read_buffer.read_long(),
            )
        )

        await cls.prepare_player(player_name)

        shared.world.config = await read_buffer.read_any()
        await shared.event_handler.call_async("seed:set")

        dimensions = await read_buffer.read_dict(
            read_buffer.read_int, read_buffer.read_string
        )
        current_dimension = read_buffer.read_int()

        await cls.prepare_mods(mods, save_file)

        # the chunks scheduled for generation
        await cls.prepare_generating_chunks(chunks_to_generate)

        await cls.prepare_dimensions(dimensions)

        if shared.IS_CLIENT:
            await shared.world.join_dimension_async(current_dimension)

        default_noise_implementation = read_buffer.read_string()
        await shared.world_generation_handler.deserialize_chunk_generator_info(
            read_buffer
        )
        await mcpython.server.worldgen.noise.NoiseManager.manager.deserialize_seed_map(
            read_buffer
        )
        mcpython.server.worldgen.noise.NoiseManager.manager.set_noise_implementation()

    @classmethod
    async def prepare_mods(cls, mods, save_file):
        for modname in mods:
            if modname not in shared.mod_loader.mods:
                logger.println(
                    "[WARNING] mod '{}' is missing. This may break your world!".format(
                        modname
                    )
                )
            elif shared.mod_loader.mods[modname].version != tuple(mods[modname]):
                try:
                    await save_file.apply_mod_fixer_async(modname, tuple(mods[modname]))
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    if modname != "minecraft":
                        logger.println(
                            "[WARN] mod {} did not provide data-fixers for mod version change "
                            "which occur between the sessions (from {} to {})".format(
                                modname,
                                tuple(mods[modname]),
                                shared.mod_loader.mods[modname].version,
                            )
                        )
        # apply data fixers for creating mod data
        for modname in shared.mod_loader.mods:
            if modname not in mods:
                try:
                    await save_file.apply_mod_fixer_async(modname, None)
                except mcpython.common.world.SaveFile.DataFixerNotFoundException:
                    pass

    @classmethod
    async def prepare_generating_chunks(cls, chunks_to_generate):
        [
            shared.world_generation_handler.add_chunk_to_generation_list(
                e[0], dimension=e[1]
            )
            for e in chunks_to_generate
        ]

    @classmethod
    async def prepare_dimensions(cls, dimensions):
        for dimension in shared.world.dimensions.values():
            if dimension.id in dimensions:
                if dimensions[dimension.id] != dimension.name:
                    logger.println(
                        "[WARN] dimension name changed for dim {} from '{}' to '{}'".format(
                            dimension.id,
                            dimensions[dimension.id],
                            dimension.name,
                        )
                    )
                del dimensions[dimension.id]
            else:
                logger.println(
                    "[WARN] dimension {} not arrival in save".format(dimension.id)
                )
        for dim in dimensions:
            logger.println(
                "[WARN] dimension {} named '{}' is arrival in save but not registered in game".format(
                    dim, dimensions[dim]
                )
            )

    @classmethod
    async def prepare_player(cls, player_name: str):
        try:
            await mcpython.util.getskin.download_skin(player_name, shared.build + "/skin.png")
        except ValueError:
            logger.println(
                "[ERROR] failed to receive skin for '{}'. Falling back to default".format(
                    player_name
                )
            )
            (
                await mcpython.engine.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                )
            ).save(shared.build + "/skin.png")
        try:
            await mcpython.common.entity.PlayerEntity.PlayerEntity.RENDERER.reload()
        except AttributeError:
            pass

    @classmethod
    async def save(cls, data, save_file):
        target_buffer = WriteBuffer()

        target_buffer.write_ulong(save_file.version)
        target_buffer.write_ulong(mcpython.common.config.VERSION_ID)
        target_buffer.write_string(
            shared.world.get_active_player().name if shared.IS_CLIENT else ""
        )

        await target_buffer.write_dict(
            shared.mod_loader.mods,
            target_buffer.write_string,
            lambda e: target_buffer.write_any(e.version),
        )
        await target_buffer.write_list(
            shared.world_generation_handler.task_handler.chunks,
            lambda chunk: target_buffer.write_int(
                chunk.get_dimension().get_dimension_id()
            )
            .write_long(chunk.get_position()[0])
            .write_long(chunk.get_position()[1]),
        )

        await target_buffer.write_any(shared.world.config)
        await target_buffer.write_dict(
            shared.world.dimensions,
            target_buffer.write_int,
            lambda e: target_buffer.write_string(e.get_name()),
        )
        target_buffer.write_int(
            shared.world.get_active_player().dimension.get_dimension_id()
            if shared.IS_CLIENT
            else 0
        )

        target_buffer.write_string(
            mcpython.server.worldgen.noise.NoiseManager.manager.default_implementation
        )
        await shared.world_generation_handler.serialize_chunk_generator_info(
            target_buffer
        )
        await mcpython.server.worldgen.noise.NoiseManager.manager.serialize_seed_map(
            target_buffer
        )

        await save_file.dump_via_network_buffer("level.dat", target_buffer)
