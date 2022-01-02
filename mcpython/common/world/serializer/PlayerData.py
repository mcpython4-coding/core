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
import asyncio

import typing

import mcpython.common.world.datafixers.IDataFixer
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer
from mcpython.engine.network.util import WriteBuffer


@shared.registry
class PlayerData(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:player_data"

    FILE_VERSION = 0

    @classmethod
    async def fix_buffer(cls, version: int, buffer: ReadBuffer):
        raise NotImplementedError

    @classmethod
    async def load(cls, save_file, **_):
        buffer: ReadBuffer = await save_file.access_via_network_buffer("players.dat")

        if buffer is None:
            return

        version = buffer.read_uint()

        if version != cls.FILE_VERSION:
            await cls.fix_buffer(version, buffer)

        players = await buffer.collect_list(lambda: buffer.read_bytes())

        current_player = shared.world.get_active_player().name if shared.IS_CLIENT else None

        async def load_player(player_data: bytes):
            player_buffer = ReadBuffer(player_data)
            player_name = player_buffer.read_string()

            if not shared.IS_CLIENT or player_name == current_player:
                player = await shared.world.get_player_by_name_async(player_name)
                await player.read_from_network_buffer(player_buffer)

        await asyncio.gather(*(load_player(player_data) for player_data in players))

    @classmethod
    async def save(cls, data, save_file, **_):
        buffer: ReadBuffer = await save_file.access_via_network_buffer("players.dat")

        if buffer is None:
            players = []
        else:
            version = buffer.read_uint()

            if version != cls.FILE_VERSION:
                await cls.fix_buffer(version, buffer)

            players = await buffer.collect_list(lambda: buffer.read_bytes())

        player_names = [ReadBuffer(e).read_string() for e in players]

        async def assemble_player_data(player) -> typing.Tuple[int, bytes]:
            p_buffer = WriteBuffer()
            p_buffer.write_string(player.name)
            await player.write_to_network_buffer(p_buffer)
            data = p_buffer.get_data()

            if player.name in player_names:
                return player_names.index(player.name), data
            else:
                return -1, data

        additional = await asyncio.gather(*(assemble_player_data(p) for p in shared.world.players.values()))

        for index, data in additional:
            if index == -1:
                players.append(data)
            else:
                players[index] = data

        write_buffer = WriteBuffer()
        write_buffer.write_uint(cls.FILE_VERSION)
        await write_buffer.write_list(players, lambda e: write_buffer.write_bytes(e))

        await save_file.dump_via_network_buffer("players.dat", write_buffer)
