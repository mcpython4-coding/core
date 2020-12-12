"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.storage.serializer.IDataSerializer
import mcpython.server.storage.datafixers.IDataFixer
from mcpython import shared as G
import time


class PlayerDataFixer(mcpython.server.storage.datafixers.IDataFixer.IPartFixer):
    """
    fixer for fixing player data
    """

    TARGET_SERIALIZER_NAME = "minecraft:player_data"

    @classmethod
    def fix(cls, savefile, player, data) -> dict:
        """
        will apply the fix
        :param savefile: the savefile to use
        :param player: the player used or None if not provided
        :param data: the data used
        :return: the fixed data
        """


@G.registry
class PlayerData(mcpython.server.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:player_data"

    @classmethod
    def apply_part_fixer(cls, savefile, fixer):
        if issubclass(fixer, PlayerDataFixer):
            data = savefile.access_file_json("players.json")
            for name in data:
                pdata = data[name]
                player = G.world.players[name] if name not in G.world.players else None
                pdata = fixer.fix(savefile, player, pdata)
                data[name] = pdata
            savefile.dump_file_json("players.json", data)

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("players.json")
        if data is not None and G.world.get_active_player().name in data:
            player = G.world.get_active_player()
            pd = data[player.name]
            player.set_gamemode(pd["gamemode"])
            player.hearts = pd["hearts"]
            player.hunger = pd["hunger"]
            player.xp = pd["xp"]
            player.xp_level = pd["xp level"]
            player.fallen_since_y = pd["fallen since y"]
            player.active_inventory_slot = pd["active inventory slot"]
            player.position = pd["position"]
            player.rotation = pd["rotation"]
            G.world.join_dimension(pd["dimension"])
            G.world.get_active_player().flying = pd["flying"]
            for i, (name, inventory) in enumerate(
                zip(pd["inventory_data"], player.get_inventories())
            ):
                savefile.read(
                    "minecraft:inventory",
                    inventory=inventory,
                    path="players/{}/inventory/{}".format(player.name, i),
                )
            if "dimension_data" in pd:
                if (
                    pd["dimension_data"]["nether_portal"]["portal_inner_time"]
                    is not None
                ):
                    player.in_nether_portal_since = (
                        time.time()
                        - pd["dimension_data"]["nether_portal"]["portal_inner_time"]
                    )
                player.should_leave_nether_portal_before_dim_change = pd[
                    "dimension_data"
                ]["nether_portal"]["portal_need_leave_before_change"]

    @classmethod
    def save(cls, data, savefile):
        data = savefile.access_file_json("players.json")
        if data is None:
            data = {}
        for player in G.world.players.values():
            # todo: move to player custom save data
            data[player.name] = {
                "position": player.position,
                "rotation": player.rotation,
                "dimension": G.world.get_active_player().dimension.id,
                "gamemode": player.gamemode,
                "hearts": player.hearts,
                "hunger": player.hunger,
                "xp": player.xp,
                "xp level": player.xp_level,
                "fallen since y": player.fallen_since_y,
                "active inventory slot": player.active_inventory_slot,
                "flying": G.world.get_active_player().flying,
                "dimension_data": {
                    "nether_portal": {
                        "portal_inner_time": None
                        if player.in_nether_portal_since is None
                        else time.time() - player.in_nether_portal_since,
                        "portal_need_leave_before_change": player.should_leave_nether_portal_before_dim_change,
                    }
                },
                "inventory_data": [
                    inventory.uuid.int for inventory in player.get_inventories()
                ],
            }
            [
                savefile.dump(
                    None,
                    "minecraft:inventory",
                    inventory=inventory,
                    path="players/{}/inventory/{}".format(player.name, i),
                )
                for i, inventory in enumerate(player.get_inventories())
            ]
        savefile.dump_file_json("players.json", data)
