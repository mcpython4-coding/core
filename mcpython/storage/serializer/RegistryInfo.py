"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.storage.serializer.IDataSerializer
import globals as G
import logger


@G.registry
class RegistryInfo(mcpython.storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:registry_info_serializer"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_pickle("registries.dat")
        if data is None: return
        for registry in G.registry.registries:
            if not registry.dump_content_in_saves: continue
            if registry.name not in data:
                logger.println("[REGISTRY][WARN] registry '{}' not found in files!".format(registry.name))
            else:
                entries = data[registry.name]
                del data[registry.name]
                for obj in registry.registered_object_map.values():
                    compressed = obj.compressed_info()
                    if compressed not in entries:
                        logger.println("[REGISTRY][WARN] object '{}' in registry '{}' not found in saves!".format(
                            obj.NAME, registry.name))
                    else:
                        entries.remove(compressed)
                for compressed in entries:
                    logger.println("[REGISTRY][WARN] compressed info '{}' for registry '{}' found in saves, but not in"
                                   " active registry".format(compressed, registry.name))
        for name in data:
            logger.println("[REGISTRY][WARN] registry '{}' found in saves, but it is not arrival anymore".format(name))

    @classmethod
    def save(cls, data, savefile):
        data = {}
        for registry in G.registry.registries:
            rdata = []
            for obj in registry.registered_object_map.values(): rdata.append(obj.compressed_info())
            data[registry.name] = rdata
        savefile.dump_file_pickle("registries.dat", data)

