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
import re
import typing

import mcpython.common.data.serializer.DataSerializationManager
import mcpython.util.data
from mcpython import shared
from mcpython.engine import logger
from mcpython.common.data.serializer.DataSerializationManager import ISerializeAble


class WorldGenerationModeModifier(
    mcpython.common.data.serializer.DataSerializationManager.ISerializer
):
    BIOME_SOURCES: typing.Dict[str, typing.Type] = {}

    @classmethod
    def deserialize(cls, data: dict) -> dict:
        return data

    @classmethod
    def serialize(cls, obj: typing.Type[ISerializeAble]) -> dict:
        raise NotImplementedError()

    @classmethod
    def register(cls, data: dict):
        mode = shared.world_generation_handler.get_world_gen_config(
            data["dimension"], data["name"]
        )
        if "biomes" in data:
            for mass in data["biomes"]:
                for temp in data["biomes"][mass]:
                    biomes = data["biomes"][mass][temp]
                    biome_list = mode.BIOMES.setdefault(mass, {}).setdefault(temp, [])
                    for entry in biomes:
                        if entry.startswith("-"):
                            entry = entry[1:]
                            if entry in biome_list:
                                biome_list.remove(entry)
                            else:
                                logger.println(
                                    "could not find biome {} for modifier {}, skipping...".format(
                                        entry, data
                                    )
                                )
                        elif entry not in biome_list:
                            biome_list.append(entry)

        if "landmasses" in data:
            for mass in data["landmasses"]:
                if mass.startswith("-"):
                    mass = mass[1:]
                    if mass in mode.LANDMASSES:
                        mode.LANDMASSES.remove(mass)
                elif mass not in mode.LANDMASSES:
                    mode.LANDMASSES.append(mass)

        if "layers" in data:
            for layer in data["layers"]:
                if type(layer) == str:
                    if layer.startswith("-"):
                        layer = layer[1:]
                        if layer in mode.LAYERS:
                            mode.LAYERS.remove(layer)
                    elif layer not in mode.LAYERS:
                        mode.LAYERS.append(layer)

                else:
                    if "remove" in layer:
                        del data["remove"]
                        if layer in mode.LAYERS:
                            mode.LAYERS.remove(layer)
                    else:
                        mode.LAYERS.append(layer)

    @classmethod
    def clear(cls):
        pass


instance = (
    mcpython.common.data.serializer.DataSerializationManager.DataSerializationService(
        "minecraft:world_gen_mode_modifiers",
        re.compile("data/[A-Za-z0-9-_]+/worldgen/mode_modifiers/[A-Za-z0-9-_/]+.json"),
        data_deserializer=mcpython.util.data.bytes_to_json,
        data_serializer=mcpython.util.data.json_to_bytes,
        re_run_on_reload=True,
    ).register_serializer(WorldGenerationModeModifier)
)
instance.on_deserialize = WorldGenerationModeModifier.register
instance.on_unload = WorldGenerationModeModifier.clear
instance.register_listener()
