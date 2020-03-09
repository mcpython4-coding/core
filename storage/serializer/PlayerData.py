"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import storage.serializer.IDataSerializer
import globals as G


@G.registry
class PlayerData(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:player_data"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_json("players.json")
        if data is not None and G.player.name in data:
            pd = data[G.player.name]
            G.player.set_gamemode(pd["gamemode"])
            G.player.hearts = pd["hearts"]
            G.player.hunger = pd["hunger"]
            G.player.xp = pd["xp"]
            G.player.xp_level = pd["xp level"]
            G.player.fallen_since_y = pd["fallen since y"]
            G.player.active_inventory_slot = pd["active inventory slot"]
            G.player.position = pd["position"]
            G.player.rotation = pd["rotation"]
            G.world.join_dimension(pd["dimension"], save_current=False)
            G.window.flying = pd["flying"]
            for name in pd["inventory links"]:
                savefile.read("minecraft:inventory", inventory=G.player.inventorys[name],
                              path="players/{}/inventory/{}".format(G.player.name, name))

    @classmethod
    def save(cls, data, savefile):
        data = savefile.access_file_json("players.json")
        if data is None: data = {}
        data[G.player.name] = {
            "position": G.player.position,
            "rotation": G.player.rotation,
            "dimension": G.world.active_dimension,
            "gamemode": G.player.gamemode,
            "hearts": G.player.hearts,
            "hunger": G.player.hunger,
            "xp": G.player.xp,
            "xp level": G.player.xp_level,
            "fallen since y": G.player.fallen_since_y,
            "active inventory slot": G.player.active_inventory_slot,
            "flying": G.window.flying,
            "inventory links": {name: G.player.inventorys[name].uuid.int for name in G.player.inventorys}
        }
        [savefile.dump(None, "minecraft:inventory", inventory=G.player.inventorys[name],
                       path="players/{}/inventory/{}".format(G.player.name, name)) for name in G.player.inventorys]
        savefile.dump_file_json("players.json", data)

