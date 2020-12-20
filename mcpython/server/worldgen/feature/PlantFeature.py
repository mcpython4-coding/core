import mcpython.server.worldgen.feature.IFeature


class PlantFeature(mcpython.server.worldgen.feature.IFeature.IFeature):
    def __init__(self):
        self.plants = []

    def add_plant(self, plant: str, weight: int):
        self.plants.append((plant, weight))
        return self
