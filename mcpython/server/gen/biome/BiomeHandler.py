"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G
import mcpython.common.mod.ModMcpython


class BiomeHandler:
    def __init__(self):
        self.registrylist = []
        self.biomes = {}
        self.biometable = (
            {}
        )  # {dim: int -> {landmass: str -> {temperature: int -> [biomename with weights]}}}}

    def register(self, biome, dimensions=[]):
        self(biome)
        for dim in dimensions:
            self.add_biome_to_dim(dim, biome.NAME)

    def __call__(self, biome):
        if biome in self.biomes.values():
            raise ValueError("can't add biome. biome is in biome registry")
        self.biomes[biome.NAME] = biome
        self.registrylist.append(biome)

    def add_biome_to_dim(self, dim: int, biomename: str):
        biome = self.biomes[biomename]
        if dim not in self.biometable:
            self.biometable[dim] = {}
        if biome.get_landmass() not in self.biometable[dim]:
            self.biometable[dim][biome.get_landmass()] = {}
        if biome.get_temperature() not in self.biometable[dim][biome.get_landmass()]:
            self.biometable[dim][biome.get_landmass()][biome.get_temperature()] = []
        self.biometable[dim][biome.get_landmass()][biome.get_temperature()] += [
            biomename
        ] * biome.get_weight()

    def remove_biome_from_dim(self, dim: int, biomename: str):
        biome = self.biomes[biomename]
        while biomename in self.biometable[dim][biome.get_landmass()]:
            self.biometable[dim][biome.get_landmass()][biome.get_temperature()].remove(
                biomename
            )

    def is_biome_in_dim(self, dim: int, biomename: str):
        return any(
            [
                biomename in x
                for x in self.biometable[dim][
                    self.biomes[biomename].get_landmass()
                ].values()
            ]
        )

    def get_biomes_for_dimension(
        self, dim: int, landmass: str, weighted=False, temperature=None
    ) -> list:
        if temperature is None:
            l = []
            for ll in self.biometable[dim][landmass]:
                l += ll
        else:
            if temperature not in self.biometable[dim][landmass]:
                return []
            l = self.biometable[dim][landmass][temperature]
        return list(tuple(l)) if not weighted else l

    def get_sum_weight_count(self, dim: int, landmass: str, temperature=None) -> int:
        return len(
            self.get_biomes_for_dimension(
                dim, landmass, weighted=True, temperature=temperature
            )
        )

    def get_biome_at(
        self, landmass: str, dim: int, selectvalue: float, temperature: float
    ) -> str:
        """
        gets an biome with given info
        :param landmass: the landmass to choise from
        :param dim: the dimension we were in
        :param selectvalue: an value with which the system decides which biome to select, value from 0. - 1.
        :param temperature: the temperature to use
        :return: the biome which was selected
        """
        temperatures = list(self.biometable[dim][landmass].keys())
        temperatures.sort(key=lambda x: abs(temperature - x))
        temperature = temperatures[0]
        biomes = self.get_biomes_for_dimension(
            dim, landmass, weighted=True, temperature=temperature
        )
        selectvalue *= len(biomes)
        selectvalue = round(selectvalue)
        if selectvalue == len(biomes):
            selectvalue = 0
        return biomes[selectvalue]


G.biomehandler = BiomeHandler()


def load():
    from . import BiomePlains


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:worldgen:biomes", load, info="loading biomes"
)
