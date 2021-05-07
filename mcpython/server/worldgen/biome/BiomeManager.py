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
import itertools
import typing

import mcpython.common.mod.ModMcpython
import mcpython.server.worldgen.biome.Biome
import mcpython.server.worldgen.feature.IFeature
from mcpython import shared


class BiomeHandler:
    """
    The main handler for biomes
    Stores needed maps for the lookup during biome generation

    todo: make proper registry for biomes as everything is now data-driven-able, and as such depends not on a custom
        register function
    todo: maybe use instances for dynamic constructed biomes?
    """

    def __init__(self):
        self.registry_list = []
        self.biomes = {}
        self.biome_table: typing.Dict[
            int, typing.Dict[str, typing.Dict[int, typing.List[str]]]
        ] = (
            {}
        )  # {dim: int -> {landmass: str -> {temperature: int -> [biome-name with weights]}}}}

    def register(self, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome]):
        self(biome)

    @classmethod
    def setup_biome_feature_list(
        cls, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome], force=False
    ):
        """
        Helper function for recalculating the internal biome feature sorted array
        :param biome: the biome
        :param force: force-recalculate?
        """
        if biome.FEATURES_SORTED is None or force:
            biome.FEATURES_SORTED = {}
            for feature_def in biome.FEATURES:
                feature_def: mcpython.server.worldgen.feature.IFeature.FeatureDefinition
                biome.FEATURES_SORTED.setdefault(
                    feature_def.group, (feature_def.group_spawn_count, 0, [], [])
                )[3].append(feature_def)
                data = biome.FEATURES_SORTED[feature_def.group]
                biome.FEATURES_SORTED[feature_def.group] = (
                    data[0],
                    data[1] + feature_def.weight,
                    data[2] + [feature_def.weight],
                    data[3],
                )

            for group in biome.FEATURES_SORTED:
                data = biome.FEATURES_SORTED[group]
                biome.FEATURES_SORTED[group] = (
                    data[0],
                    data[1],
                    list(itertools.accumulate(data[2])),
                    data[3],
                )

    def __call__(self, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome]):
        """
        Registers a biome to the internal system
        Will setup the FEATURES_SORTED system for later lookup
        :param biome: the biome to register
        :return: the biome, for @BiomeHandler-ing
        """
        self.setup_biome_feature_list(biome)

        if biome in self.biomes.values():
            raise ValueError("can't add biome. biome is in biome registry")
        self.biomes[biome.NAME] = biome
        self.registry_list.append(biome)
        return biome

    def unregister(
        self, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome]
    ):
        if biome.NAME in self.biomes:
            del self.biomes[biome.NAME]
            self.registry_list.remove(biome)

    @classmethod
    def get_biomes_for_dimension(
        cls, biomes: typing.Dict[int, str], weighted=False, temperature=None
    ) -> list:
        if temperature is None:
            biomes = []
            for ll in biomes:
                biomes += ll
        else:
            if temperature not in biomes:
                return []
            biomes = biomes[temperature]

        return list(tuple(biomes)) if not weighted else biomes

    def get_sum_weight_count(self, biomes, temperature=None) -> int:
        return len(
            self.get_biomes_for_dimension(
                biomes, weighted=True, temperature=temperature
            )
        )

    def get_biome_at(
        self,
        landmass: str,
        select_value: float,
        temperature: float,
        biomes: typing.Dict[str, typing.Dict[int, str]],
    ) -> str:
        """
        Gets an biome with given info
        :param landmass: the landmass to chose from
        :param select_value: an value with which the system decides which biome to select, value from 0. - 1.
        :param temperature: the temperature to use
        :param biomes: the biomes to select from
        :return: the biome which was selected
        """
        temperatures = list(biomes[landmass].keys())
        temperatures.sort(key=lambda x: abs(temperature - x))
        temperature = temperatures[0]
        biomes = self.get_biomes_for_dimension(
            biomes[landmass], weighted=True, temperature=temperature
        )
        select_value *= len(biomes)
        select_value = round(select_value)
        if select_value == len(biomes):
            select_value = 0
        return biomes[select_value]


shared.biome_handler = BiomeHandler()


def load():
    from . import BiomeMountains, BiomeVoid


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:biomes", load, info="loading biomes"
)
