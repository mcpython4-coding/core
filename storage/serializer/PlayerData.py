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
        if data is not None and G.world.get_active_player().name in data:
            pd = data[G.world.get_active_player().name]
            G.world.get_active_player().set_gamemode(pd["gamemode"])
            G.world.get_active_player().hearts = pd["hearts"]
            G.world.get_active_player().hunger = pd["hunger"]
            G.world.get_active_player().xp = pd["xp"]
            G.world.get_active_player().xp_level = pd["xp level"]
            G.world.get_active_player().fallen_since_y = pd["fallen since y"]
            G.world.get_active_player().active_inventory_slot = pd["active inventory slot"]
            G.world.get_active_player().position = pd["position"]
            G.world.get_active_player().rotation = pd["rotation"]
            G.world.join_dimension(pd["dimension"], save_current=False)
            G.window.flying = pd["flying"]
            for name in pd["inventory links"]:
                savefile.read("minecraft:inventory", inventory=G.world.get_active_player().inventories[name],
                              path="players/{}/inventory/{}".format(G.world.get_active_player().name, name))

    @classmethod
    def save(cls, data, savefile):
        data = savefile.access_file_json("players.json")
        if data is None: data = {}
        data[G.world.get_active_player().name] = {
            "position": G.world.get_active_player().position,
            "rotation": G.world.get_active_player().rotation,
            "dimension": G.world.active_dimension,
            "gamemode": G.world.get_active_player().gamemode,
            "hearts": G.world.get_active_player().hearts,
            "hunger": G.world.get_active_player().hunger,
            "xp": G.world.get_active_player().xp,
            "xp level": G.world.get_active_player().xp_level,
            "fallen since y": G.world.get_active_player().fallen_since_y,
            "active inventory slot": G.world.get_active_player().active_inventory_slot,
            "flying": G.window.flying,
            "inventory links": {name: G.world.get_active_player().inventories[name].uuid.int for name in G.world.get_active_player().inventories}
        }
        [savefile.dump(None, "minecraft:inventory", inventory=G.world.get_active_player().inventories[name],
                       path="players/{}/inventory/{}".format(G.world.get_active_player().name, name)) for name in G.world.get_active_player().inventories]
        savefile.dump_file_json("players.json", data)

