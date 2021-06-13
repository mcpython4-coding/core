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
from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class World(NativeClass):
    NAME = "net/minecraft/world/World"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_234918_g_": None,
                "field_234919_h_": None,
                "field_234920_i_": None,
                "field_239699_ae_": None,
            }
        )


class Structure(NativeClass):
    NAME = "net/minecraft/world/gen/feature/structure/Structure"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_236365_a_": None,
            }
        )

    @native(
        "func_236391_a_",
        "(Lnet/minecraft/world/gen/feature/IFeatureConfig;)Lnet/minecraft/world/gen/feature/StructureFeature;",
    )
    def func_236391_a_(self, instance, config):
        pass

    @native("<init>", "(Lcom/mojang/serialization/Codec;)V")
    def init(self, *_):
        pass


class DimensionStructuresSettings(NativeClass):
    NAME = "net/minecraft/world/gen/settings/DimensionStructuresSettings"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_236191_b_": None,
            }
        )


class StructureSeparationSettings(NativeClass):
    NAME = "net/minecraft/world/gen/settings/StructureSeparationSettings"

    @native("<init>", "(III)V")
    def init(self, instance, x, y, z):
        pass


class FlatGenerationSettings(NativeClass):
    NAME = "net/minecraft/world/gen/FlatGenerationSettings"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_202247_j": None,
            }
        )


class BiomeGeneratorTypeScreens(NativeClass):
    NAME = "net/minecraft/client/gui/screen/BiomeGeneratorTypeScreens"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_239068_c_": None,
            }
        )

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, v: str):
        pass


class Feature(NativeClass):
    NAME = "net/minecraft/world/gen/feature/Feature"

    @native("<init>", "(Lcom/mojang/serialization/Codec;)V")
    def init(self, instance, codec):
        pass

    @native(
        "func_225566_b_",
        "(Lnet/minecraft/world/gen/feature/IFeatureConfig;)Lnet/minecraft/world/gen/feature/ConfiguredFeature;",
    )
    def func_225566_b_(self, instance, config):
        return instance

    @native(
        "func_227228_a_",
        "(Lnet/minecraft/world/gen/placement/ConfiguredPlacement;)Lnet/minecraft/world/gen/feature/ConfiguredFeature;",
    )
    def func_227228_a_(self, instance, config):
        return instance


class ConfiguredFeature(NativeClass):
    NAME = "net/minecraft/world/gen/feature/ConfiguredFeature"

    @native(
        "func_227228_a_",
        "(Lnet/minecraft/world/gen/placement/ConfiguredPlacement;)Lnet/minecraft/world/gen/feature/ConfiguredFeature;",
    )
    def func_227228_a_(self, *_):
        pass


class NoFeatureConfig(NativeClass):
    NAME = "net/minecraft/world/gen/feature/NoFeatureConfig"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_236558_a_": None,
                "field_236559_b_": None,
            }
        )


class Placement(NativeClass):
    NAME = "net/minecraft/world/gen/placement/Placement"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_215022_h": 0,
            }
        )

    @native(
        "func_227446_a_",
        "(Lnet/minecraft/world/gen/placement/IPlacementConfig;)Lnet/minecraft/world/gen/placement/ConfiguredPlacement;",
    )
    def func_227446_a_(self, instance, config):
        pass


class IPlacementConfig(NativeClass):
    NAME = "net/minecraft/world/gen/placement/IPlacementConfig"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"field_202468_e": None})


class Biome__Category(NativeClass):
    NAME = "net/minecraft/world/biome/Biome$Category"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "NETHER": 0,
                "THEEND": 1,
                "ICY": 2,
                "MUSHROOM": 3,
                "BEACH": 4,
                "DESERT": 5,
                "EXTREME_HILLS": 6,
                "FOREST": 7,
                "JUNGLE": 8,
                "MESA": 9,
                "PLAINS": 12,
                "RIVER": 11,
                "SAVANNA": 12,
                "SWAMP": 13,
                "TAIGA": 14,
            }
        )
