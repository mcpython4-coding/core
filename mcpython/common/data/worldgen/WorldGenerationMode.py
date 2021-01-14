"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import shared
import mcpython.common.data.DataSerializerHandler
import mcpython.util.data
from mcpython.common.data.DataSerializerHandler import ISerializeAble


class WorldGenerationModeSerializer(
    mcpython.common.data.DataSerializerHandler.ISerializer
):
    COLLECTED = []
    BIOME_SOURCES: typing.Dict[str, typing.Type] = {}

    @classmethod
    def deserialize(cls, data: dict) -> typing.Type[ISerializeAble]:
        import mcpython.server.worldgen.mode.IWorldGenConfig

        class WorldGenMode(
            mcpython.server.worldgen.mode.IWorldGenConfig.IWorldGenConfig
        ):
            NAME = data["name"]
            DIMENSION = data["dimension"]
            DISPLAY_NAME = (
                data["name"] if "display_name" not in data else data["display_name"]
            )

            biome_data = data.setdefault("biomes", {})
            BIOMES = {
                mass: {
                    float(temp): data["biomes"][mass][temp]
                    for temp in data["biomes"][mass]
                }
                for mass in biome_data
            }

            biome_config = data.setdefault("biome_source", {})
            BIOME_SOURCE = cls.BIOME_SOURCES[
                biome_config.setdefault("type", "minecraft:single_biome")
            ](
                *(
                    biome_config.setdefault(
                        "args",
                        []
                        if biome_config["type"] != "minecraft:single_biome"
                        else ["minecraft:void"],
                    )
                )
            )

            LANDMASSES = data.setdefault("landmasses", [])
            LAYERS = data.setdefault("layers", [])

            GENERATES_START_CHEST = data.setdefault("generates_start_chest", False)

        return WorldGenMode

    @classmethod
    def serialize(cls, obj: typing.Type[ISerializeAble]) -> dict:
        data = {
            "name": obj.NAME,
            "dimension": obj.DIMENSION,
            "biome_source": {
                "type": filter(
                    lambda key: isinstance(obj.BIOME_SOURCE, cls.BIOME_SOURCES[key]),
                    list(cls.BIOME_SOURCES.keys()),
                )[0],
                "args": obj.BIOME_SOURCE.get_creation_args(),
            },
        }
        if obj.NAME != obj.DISPLAY_NAME:
            data["display_name"] = obj.DISPLAY_NAME

        if obj.BIOMES:
            biome_data = obj.BIOMES
            BIOMES = {
                mass: {float(temp): biome_data[mass][temp] for temp in biome_data[mass]}
                for mass in biome_data
            }
            data["biomes"] = BIOMES

        if obj.LANDMASSES:
            data["landmasses"] = obj.LANDMASSES

        if obj.LAYERS:
            data["layers"] = obj.LAYERS

        if obj.GENERATES_START_CHEST:
            data["generates_start_chest"] = obj.GENERATES_START_CHEST

        return data

    @classmethod
    def register(cls, obj: ISerializeAble):
        cls.COLLECTED.append(obj)
        shared.world_generation_handler.register_world_gen_config(obj)

    @classmethod
    def clear(cls):
        for obj in cls.COLLECTED:
            shared.world_generation_handler.unregister_world_gen_config(obj)

        cls.COLLECTED.clear()


instance = mcpython.common.data.DataSerializerHandler.DatapackSerializationHelper(
    "minecraft:world_gen_modes",
    "data/{pathname}/worldgen/modes",
    data_formatter=mcpython.util.data.bytes_to_json,
    data_un_formatter=mcpython.util.data.json_to_bytes,
    re_run_on_reload=True,
    load_on_stage="stage:worldgen:serializer:mode:load",
).register_serializer(WorldGenerationModeSerializer)
instance.on_deserialize = WorldGenerationModeSerializer.register
instance.on_clear = WorldGenerationModeSerializer.clear
