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
import mcpython.common.world.serializer.IDataSerializer
from mcpython import shared, logger


@shared.registry
class RegistryInfo(mcpython.common.world.serializer.IDataSerializer.IDataSerializer):
    """
    Serializer storing the content of various registries
    """

    PART = NAME = "minecraft:registry_info_serializer"

    @classmethod
    def load(cls, save_file):
        data = save_file.access_file_pickle("registries.dat")
        if data is None:
            return

        type_change_builder = logger.TableBuilder(header="REGISTRY TYPE CHANGES")

        registry_miss_match = {}

        for (
            registry
        ) in shared.registry.registries.values():  # iterate over all registries
            if not registry.dump_content_in_saves:
                continue

            registry_miss_match[registry.name] = []
            if registry.name not in data:
                type_change_builder.println(
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
            type_change_builder.println("missing registry: {}".format(name))

        type_change_builder.finish()
        for name in registry_miss_match:
            if len(registry_miss_match[name]) != 0:
                logger.write_into_container(
                    registry_miss_match[name],
                    header="registry {} has the following miss-matches".format(name),
                )

    @classmethod
    def save(cls, data, save_file):
        data = {}
        for registry in shared.registry.registries.values():
            if not registry.dump_content_in_saves:
                continue
            rdata = []
            for obj in registry.entries.values():
                rdata.append(obj.compressed_info())
            data[registry.name] = rdata
        save_file.dump_file_pickle("registries.dat", data)
