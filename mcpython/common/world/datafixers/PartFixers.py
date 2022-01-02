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
import mcpython.common
from mcpython import shared

from .IDataFixer import IPartFixer


class GameRuleFixer(IPartFixer):
    """
    Fixer targeting one or more game-rule entries
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to

    @classmethod
    async def fix(cls, save_file, data) -> dict:
        pass

    @classmethod
    async def apply(cls, save_file, *args):
        data = await save_file.access_file_json_async("gamerules.json")
        if data is None:
            return
        for name in data:
            if name in cls.TARGET_GAMERULE_NAME:
                data[name] = await cls.fix(save_file, data[name])
        await save_file.dump_file_json_async("gamerules.json", data)


class GameRuleRemovalFixer(IPartFixer):
    """
    Fixer targeting the removal of game-rule data from the save files
    """

    TARGET_SERIALIZER_NAME = "minecraft:gamerule"

    TARGET_GAMERULE_NAME = []  # which game rules to apply to

    @classmethod
    async def apply(cls, save_file, *args):
        data = await save_file.access_file_json_async("gamerules.json")
        if data is None:
            return
        for name in data:
            if name in cls.TARGET_GAMERULE_NAME:
                del data[name]
        await save_file.dump_file_json_async("gamerules.json", data)


class PlayerDataFixer(IPartFixer):
    """
    Fixer for fixing player data
    """

    TARGET_SERIALIZER_NAME = "minecraft:player_data"

    @classmethod
    async def fix(cls, savefile, player, data) -> dict:
        """
        will apply the fix
        :param savefile: the savefile to use
        :param player: the player used or None if not provided
        :param data: the data used
        :return: the fixed data
        """

    @classmethod
    async def apply(cls, save_file, *args):
        data = await save_file.access_file_json_async("players.json")

        for name in data:
            player_data = data[name]
            player = (
                shared.world.players[name] if name not in shared.world.players else None
            )
            player_data = await cls.fix(save_file, player, player_data)
            data[name] = player_data

        await save_file.dump_file_json_async("players.json", data)
