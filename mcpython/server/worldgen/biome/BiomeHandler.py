"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import shared as G
import mcpython.common.mod.ModMcpython


class BiomeHandler:
    def __init__(self):
        self.registry_list = []
        self.biomes = {}
        self.biome_table = (
            {}
        )  # {dim: int -> {landmass: str -> {temperature: int -> [biomename with weights]}}}}

    def register(self, biome):
        self(biome)

    def __call__(self, biome):
        if biome in self.biomes.values():
            raise ValueError("can't add biome. biome is in biome registry")
        self.biomes[biome.NAME] = biome
        self.registry_list.append(biome)

    def add_biome_to_dim(self, dim: int, biomename: str):
        biome = self.biomes[biomename]
        if dim not in self.biome_table:
            self.biome_table[dim] = {}
        if biome.get_landmass() not in self.biome_table[dim]:
            self.biome_table[dim][biome.get_landmass()] = {}
        if biome.get_temperature() not in self.biome_table[dim][biome.get_landmass()]:
            self.biome_table[dim][biome.get_landmass()][biome.get_temperature()] = []
        self.biome_table[dim][biome.get_landmass()][biome.get_temperature()] += [
            biomename
        ] * biome.get_weight()

    def remove_biome_from_dim(self, dim: int, biomename: str):
        biome = self.biomes[biomename]
        while biomename in self.biome_table[dim][biome.get_landmass()]:
            self.biome_table[dim][biome.get_landmass()][biome.get_temperature()].remove(
                biomename
            )

    def is_biome_in_dim(self, dim: int, biomename: str):
        return any(
            [
                biomename in x
                for x in self.biome_table[dim][
                    self.biomes[biomename].get_landmass()
                ].values()
            ]
        )

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
        self, landmass: str, select_value: float, temperature: float, biomes: typing.Dict[str, typing.Dict[int, str]]
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
    from . import BiomePlains, BiomeDessert, BiomeVoid


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:biomes", load, info="loading biomes"
)
