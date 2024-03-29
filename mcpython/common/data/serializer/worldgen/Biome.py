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
from abc import ABC

import mcpython.common.data.serializer.DataSerializationManager
import mcpython.engine.world.AbstractInterface
import mcpython.util.data
from mcpython import shared
from mcpython.common.data.serializer.DataSerializationManager import ISerializeAble
from mcpython.util.texture import hex_to_color


class ITopLayerConfigurator(ABC):
    NAME: str

    def __init__(self, config: dict):
        self.config = config

    def get_top_layer_height_range(
        self,
        position: typing.Tuple[int, int],
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        raise NotImplementedError()

    def get_top_layer_configuration(
        self,
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        raise NotImplementedError()


class DefaultTopLayerConfiguration(ITopLayerConfigurator):
    NAME = "minecraft:default_top_layer_config"

    def __init__(self, config: dict):
        super().__init__(config)
        flag = "blocks" in config
        config.setdefault("blocks", {})
        self.default_block = config["blocks"].setdefault("base", "minecraft:dirt")

        if not flag:
            self.top_extension = "minecraft:grass_block", 1
            self.bottom_extension = None, 0

        else:
            self.top_extension = tuple(
                config["blocks"].setdefault("top_extension", (None, 0))
            )
            self.bottom_extension = tuple(
                config["blocks"].setdefault("bottom_extension", (None, 0))
            )

        self.height_range = tuple(config.setdefault("height_range", (3, 5)))

    def get_top_layer_height_range(
        self,
        position: typing.Tuple[int, int],
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
    ) -> typing.Tuple[int, int]:
        return self.height_range

    def get_top_layer_configuration(
        self,
        height: int,
        position: typing.Tuple[int, int],
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
    ) -> typing.List[str]:
        data = [self.default_block] * height
        if self.top_extension[0] is not None:
            data[-self.top_extension[1] :] = [
                self.top_extension[0]
            ] * self.top_extension[1]

        if self.bottom_extension[0] is not None:
            data[: self.bottom_extension[1]] = [
                self.bottom_extension[1]
            ] * self.bottom_extension[1]

        return data


class BiomeSerializer(
    mcpython.common.data.serializer.DataSerializationManager.ISerializer
):
    COLLECTED = []
    TOP_LAYER_CONFIGURATORS = {}

    @classmethod
    def register_helper(cls, obj: typing.Type):
        if issubclass(obj, ITopLayerConfigurator):
            cls.TOP_LAYER_CONFIGURATORS[obj.NAME] = obj

    @classmethod
    async def deserialize(cls, data: dict) -> typing.Type[ISerializeAble]:
        import mcpython.server.worldgen.biome.Biome

        data.setdefault("top_layer", {"type": "minecraft:default_top_layer_config"})
        layer_config: ITopLayerConfigurator = cls.TOP_LAYER_CONFIGURATORS[
            data["top_layer"]["type"]
        ](data["top_layer"])

        class Biome(mcpython.server.worldgen.biome.Biome.Biome):
            NAME = data["name"]

            # name -> weight, group size
            PASSIVE_SPAWNS = mcpython.util.data.lists_to_tuples(
                data.setdefault("passive_spawns", {})
            )
            HOSTILE_SPAWNS = mcpython.util.data.lists_to_tuples(
                data.setdefault("hostile_spawns", {})
            )
            AMBIENT_SPAWNS = mcpython.util.data.lists_to_tuples(
                data.setdefault("ambient_spawns", {})
            )

            GRASS_COLOR = data.setdefault("grass_color", (91, 201, 59))
            if isinstance(GRASS_COLOR, str):
                if GRASS_COLOR.startswith("#"):
                    GRASS_COLOR = hex_to_color(GRASS_COLOR[1:])

            WATER_COLOR = data.setdefault("water_color", None)
            if isinstance(WATER_COLOR, str):
                if WATER_COLOR.startswith("#"):
                    WATER_COLOR = hex_to_color(WATER_COLOR[1:])

            FEATURES = [
                cls.decode_feature(feature)
                for feature in data.setdefault("features", [])
            ]
            FEATURES_SORTED = None

            CARVERS = []  # for the future...

            @classmethod
            def get_landmass(cls) -> str:
                return data["mass"]

            @classmethod
            def get_weight(cls) -> int:
                return data.setdefault("weight", 10)

            @classmethod
            def get_height_range(cls) -> typing.Tuple[int, int]:
                return tuple(data.setdefault("height_range", (10, 30)))

            @classmethod
            def get_top_layer_height_range(
                cls,
                position: typing.Tuple[int, int],
                dimension: mcpython.engine.world.AbstractInterface.IDimension,
            ) -> typing.Tuple[int, int]:
                return layer_config.get_top_layer_height_range(position, dimension)

            @classmethod
            def get_top_layer_configuration(
                cls,
                height: int,
                position: typing.Tuple[int, int],
                dimension: mcpython.engine.world.AbstractInterface.IDimension,
            ):
                return layer_config.get_top_layer_configuration(
                    height, position, dimension
                )

        return Biome

    @classmethod
    def decode_feature(cls, data: dict):
        feature_cls = shared.registry.get_by_name(
            "minecraft:world_gen_features"
        ).full_entries[data["type"]]
        return feature_cls.as_feature_definition(
            data["weight"],
            data["group"],
            mcpython.util.data.lists_to_tuples(data.setdefault("group_spawn_count", 0)),
            config=data.setdefault("config", {}),
        )

    @classmethod
    async def serialize(cls, obj: typing.Type[ISerializeAble]) -> dict:
        raise NotImplementedError()

    @classmethod
    async def register(cls, obj):
        cls.COLLECTED.append(obj)
        shared.biome_handler.register(obj)

    @classmethod
    def clear(cls):
        for obj in cls.COLLECTED:
            shared.biome_handler.unregister(obj)

        cls.COLLECTED.clear()


# todo: add modifier system
instance = (
    mcpython.common.data.serializer.DataSerializationManager.DataSerializationService(
        "minecraft:biomes",
        re.compile("data/[A-Za-z0-9-_]+/worldgen/biomes/[A-Za-z0-9-_/]+.json"),
        data_deserializer=mcpython.util.data.bytes_to_json_async,
        data_serializer=mcpython.util.data.json_to_bytes_async,
        re_run_on_reload=True,
    ).register_serializer(BiomeSerializer)
)
instance.on_deserialize = BiomeSerializer.register
instance.on_unload = BiomeSerializer.clear
BiomeSerializer.register_helper(DefaultTopLayerConfiguration)
instance.register_listener()
