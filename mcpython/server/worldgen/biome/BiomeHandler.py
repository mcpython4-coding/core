"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing
import itertools

from mcpython import shared as G
import mcpython.common.mod.ModMcpython
import mcpython.server.worldgen.biome.Biome
import mcpython.server.worldgen.feature.IFeature


class BiomeHandler:
    def __init__(self):
        self.registry_list = []
        self.biomes = {}
        self.biome_table: typing.Dict[
            int, typing.Dict[str, typing.Dict[int, typing.List[str]]]
        ] = (
            {}
        )  # {dim: int -> {landmass: str -> {temperature: int -> [biome-name with weights]}}}}

    def register(self, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome]):
        if biome.FEATURES_SORTED is None:
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
        self(biome)

    def unregister(
        self, biome: typing.Type[mcpython.server.worldgen.biome.Biome.Biome]
    ):
        del self.biomes[biome.NAME]
        self.registry_list.remove(biome)

    def __call__(self, biome):
        if biome in self.biomes.values():
            raise ValueError("can't add biome. biome is in biome registry")
        self.biomes[biome.NAME] = biome
        self.registry_list.append(biome)

    def get_biomes_for_dimension(
        self, biomes: typing.Dict[int, str], weighted=False, temperature=None
    ) -> list:
        if temperature is None:
            l = []
            for ll in biomes:
                l += ll
        else:
            if temperature not in biomes:
                return []
            l = biomes[temperature]
        return list(tuple(l)) if not weighted else l

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
        gets an biome with given info
        :param landmass: the landmass to choise from
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


G.biome_handler = BiomeHandler()


def load():
    from . import BiomeDessert, BiomeVoid, BiomeMountains


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:biomes", load, info="loading biomes"
)
