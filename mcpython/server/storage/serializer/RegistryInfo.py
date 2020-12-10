"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.server.storage.serializer.IDataSerializer
from mcpython import shared as G, logger


@G.registry
class RegistryInfo(mcpython.server.storage.serializer.IDataSerializer.IDataSerializer):
    """
    Serializer storing the content of various registries
    """

    PART = NAME = "minecraft:registry_info_serializer"

    @classmethod
    def load(cls, savefile):
        data = savefile.access_file_pickle("registries.dat")
        if data is None:
            return

        registry_miss_match = {}
        registry_type_changes = []

        for registry in G.registry.registries:  # iterate over all registries
            if not registry.dump_content_in_saves:
                continue
            registry_miss_match[registry.name] = []
            if registry.name not in data:
                registry_type_changes.append(
                    "registry {} not dumped in save files".format(registry.name)
                )
            else:
                entries = data[registry.name]
                del data[registry.name]
                for obj in registry.entries.values():
                    compressed = obj.compressed_info()
                    if compressed not in entries:
                        registry_miss_match[registry.name].append(
                            "new object: {}".format(obj.NAME)
                        )
                    else:
                        entries.remove(compressed)
                for compressed in entries:
                    registry_miss_match[registry.name].append(
                        "missing object: {}".format(compressed)
                    )
        for name in data:
            registry_type_changes.append("missing registry: {}".format(name))

        if len(registry_type_changes) != 0:
            logger.write_into_container(
                registry_type_changes, header="REGISTRY TYPE CHANGES"
            )
        for name in registry_miss_match:
            if len(registry_miss_match[name]) != 0:
                logger.write_into_container(
                    registry_miss_match[name],
                    header="registry {} has the following miss-matches".format(name),
                )

    @classmethod
    def save(cls, data, savefile):
        data = {}
        for registry in G.registry.registries:
            if not registry.dump_content_in_saves:
                continue
            rdata = []
            for obj in registry.entries.values():
                rdata.append(obj.compressed_info())
            data[registry.name] = rdata
        savefile.dump_file_pickle("registries.dat", data)
