import storage.serializer.IDataSerializer
import globals as G
import logger


@G.registry
class RegistryInfo(storage.serializer.IDataSerializer.IDataSerializer):
    PART = NAME = "minecraft:registry_info_serializer"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_pickle("registries.dat")
        if data is None: return
        for registry in G.registry.registries:
            if registry.name not in data:
                logger.println("[REGISTRY][WARN] registry '{}' not found in files!".format(registry.name))
            else:
                entries = data[registry.name]
                del data[registry.name]
                for obj in registry.registered_object_map.values():
                    compressed = obj.compressed_info()
                    if compressed not in entries:
                        logger.println("[REGISTRY][WARN] object '{}' not found in saves!".format(obj.NAME))
                    else:
                        entries.remove(compressed)
                for compressed in entries:
                    logger.println("[REGISTRY][WARN] compressed info '{}' found in saves, but not in active registry".
                                   format(compressed))
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

