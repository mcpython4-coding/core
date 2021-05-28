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


class Blocks(NativeClass):
    NAME = "net/minecraft/block/Blocks"

    def __init__(self):
        super().__init__()

    def get_static_attribute(self, name: str):
        if name in self.exposed_attributes: return self.exposed_attributes[name]
        return None  # todo: registry lookup when needed

    @native("func_235430_a_", "(Lnet/minecraft/block/material/MaterialColor;Lnet/minecraft/block/material/MaterialColor;)Lnet/minecraft/block/RotatedPillarBlock;")
    def func_235430_a_(self, color_a, color_b):
        pass


class AbstractBlock(NativeClass):
    NAME = "net/minecraft/block/AbstractBlock"


class AbstractBlock_Properties(NativeClass):
    NAME = "net/minecraft/block/AbstractBlock$Properties"

    @native("func_200949_a", "(Lnet/minecraft/block/material/Material;Lnet/minecraft/block/material/MaterialColor;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200949_a(self, material, material_color):
        return self.create_instance()

    @native("func_200943_b", "(F)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200943_b(self, instance, value):
        return instance

    @native("func_200947_a", "(Lnet/minecraft/block/SoundType;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def setSoundType(self, instance, sound_type):
        return instance

    @native("harvestLevel", "(I)Lnet/minecraft/block/AbstractBlock$Properties;")
    def harvestLevel(self, instance, level: int):
        return instance

    @native("harvestTool", "(Lnet/minecraftforge/common/ToolType;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def harvestTool(self, instance, tool):
        return instance

    @native("func_200950", "(Lnet/minecraft/block/AbstractBlock;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200950(self, instance, a):
        return instance

    @native("func_200950_a", "(Lnet/minecraft/block/AbstractBlock;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200950_a(self, instance):
        return instance

    @native("func_200948_a", "(FF)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200948_a(self, instance, a, b):
        return instance

    @native("func_200945_a", "(Lnet/minecraft/block/material/Material;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200945_a(self, material):
        return self.create_instance()

    @native("func_200944_c", "()Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200944_c(self, instance):
        return instance

    @native("func_235838_a_", "(Ljava/util/function/ToIntFunction;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_235838_a_(self, instance, method):
        return instance

    @native("func_200942_a", "()Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200942_a(self, instance):
        return instance

    @native("func_200946_b", "()Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200946_b(self, instance):
        return instance

    @native("func_226896_b_", "()Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_226896_b_(self, instance):
        return instance

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, value, blockstate):
        pass


class SoundType(NativeClass):
    NAME = "net/minecraft/block/SoundType"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_185855_h": None,
            "field_185850_c": None,
            "field_185848_a": None,
        })

    @native("<init>", "(FFLnet/minecraft/util/SoundEvent;Lnet/minecraft/util/SoundEvent;Lnet/minecraft/util/SoundEvent;Lnet/minecraft/util/SoundEvent;Lnet/minecraft/util/SoundEvent;)V")
    def init(self, instance, a, b, c, d, e, f, g):
        pass


class SoundEvents(NativeClass):
    NAME = "net/minecraft/util/SoundEvents"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_187872_fl": None,
            "field_187888_ft": None,
            "field_187884_fr": None,
            "field_187878_fo": None,
            "field_187876_fn": None,
            "field_187581_bW": None,
            "field_187668_ca": None,
            "field_187587_bZ": None,
            "field_187585_bY": None,
            "field_187583_bX": None,
            "field_211419_ds": None,
            "field_211423_dw": None,
            "field_211422_dv": None,
            "field_211421_du": None,
            "field_211420_dt": None,
            "field_187561_bM": None,
            "field_187569_bQ": None,
            "field_187567_bP": None,
            "field_187565_bO": None,
            "field_187563_bN": None,
        })


class ToolType(NativeClass):
    NAME = "net/minecraftforge/common/ToolType"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "SHOVEL": "net/minecraft/block/ToolType::SHOVEL",
            "PICKAXE": "net/minecraft/block/ToolType::PICKAXE",
            "AXE": "net/minecraft/block/ToolType::AXE"
        })


class Block(AbstractBlock):
    NAME = "net/minecraft/block/Block"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass

    @native("func_176223_P", "()Lnet/minecraft/block/BlockState;")
    def func_176223_P(self, instance):
        pass

    @native("setRegistryName", "(Ljava/lang/String;)Lnet/minecraftforge/registries/IForgeRegistryEntry;")
    def setRegistryName(self, instance, name: str):
        return instance

    @native("func_208617_a", "(DDDDDD)Lnet/minecraft/util/math/shapes/VoxelShape;")
    def func_208617_a(self, *v):
        pass

    @native("func_235697_s_", "()Lnet/minecraft/block/material/MaterialColor;")
    def getMaterialColor(self, instance):
        pass

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class Material(NativeClass):
    NAME = "net/minecraft/block/material/Material"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_151595_p": None,
            "field_151576_e": None,
            "field_151578_c": None,
            "field_151577_b": None,
            "field_151583_m": None,
            "field_151592_s": None,
            "field_151575_d": None,
            "field_151585_k": None,
            "field_151584_j": None,
            "field_151594_q": None,
            "field_151582_l": None,
            "field_204868_h": None,
            "field_203243_f": None,
        })


class MaterialColor(NativeClass):
    NAME = "net/minecraft/block/material/MaterialColor"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_151677_p": None,
            "field_151676_q": None,
            "field_151646_E": None,
            "field_193573_Y": None,
            "field_151663_o": None,
            "field_193559_aa": None,
            "field_241540_ac_": None,
            "field_151648_G": None,
            "field_151653_I": None,
            "field_193565_Q": None,
            "field_193562_N": None,
            "field_151645_D": None,
            "field_193561_M": None,
            "field_197655_T": None,
            "field_151666_j": None,
            "field_151671_v": None,
            "field_193567_S": None,
            "field_151664_l": None,
            "field_151678_z": None,
            "field_151654_J": None,
            "field_193566_R": None,
            "field_151665_m": None,
            "field_151670_w": None,
            "field_151679_y": None,
            "field_151649_A": None,
            "field_193564_P": None,
            "field_193572_X": None,
            "field_193571_W": None,
            "field_193568_T": None,
            "field_197656_x": None,
            "field_151675_r": None,
            "field_151655_K": None,
        })


class FireBlock(Block):
    NAME = "net/minecraft/block/FireBlock"

    @native("func_180686_a", "(Lnet/minecraft/block/Block;II)V")
    def func_180686_a(self, instance, block_class, a, b):
        pass


class ComposterBlock(Block):
    NAME = "net/minecraft/block/ComposterBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_220299_b": {}
        })


class SandBlock(Block):
    NAME = "net/minecraft/block/SandBlock"

    @native("<init>", "(ILnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, value, properties):
        pass


class StairsBlock(Block):
    NAME = "net/minecraft/block/StairsBlock"

    @native("<init>", "(Lnet/minecraft/block/BlockState;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, a, properties):
        pass


class SlabBlock(Block):
    NAME = "net/minecraft/block/SlabBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class WallBlock(Block):
    NAME = "net/minecraft/block/WallBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class GrassBlock(Block):
    NAME = "net/minecraft/block/GrassBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class HorizontalFaceBlock(Block):
    NAME = "net/minecraft/block/HorizontalFaceBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_196366_M": None,
            "field_185512_D": None,
        })

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class HugeMushroomBlock(Block):
    NAME = "net/minecraft/block/HugeMushroomBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class SaplingBlock(Block):
    NAME = "net/minecraft/block/SaplingBlock"

    @native("<init>", "(Lnet/minecraft/block/trees/Tree;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, tree, properties):
        pass

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, block_state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class LeavesBlock(Block):
    NAME = "net/minecraft/block/LeavesBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class RotatedPillarBlock(Block):
    NAME = "net/minecraft/block/RotatedPillarBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class FenceBlock(Block):
    NAME = "net/minecraft/block/FenceBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class FenceGateBlock(Block):
    NAME = "net/minecraft/block/FenceGateBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class DoorBlock(Block):
    NAME = "net/minecraft/block/DoorBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class TrapDoorBlock(Block):
    NAME = "net/minecraft/block/TrapDoorBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class PressurePlateBlock(Block):
    NAME = "net/minecraft/block/PressurePlateBlock"

    @native("<init>", "(Lnet/minecraft/block/PressurePlateBlock$Sensitivity;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, sensitivity, properties):
        pass


class PressurePlateBlock_Sensitivity(NativeClass):
    NAME = "net/minecraft/block/PressurePlateBlock$Sensitivity"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "EVERYTHING": "net/minecraft/block/PressurePlateBlock$Sensitivity::EVERYTHING"
        })


class WoodButtonBlock(Block):
    NAME = "net/minecraft/block/WoodButtonBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class FlowerBlock(Block):
    NAME = "net/minecraft/block/FlowerBlock"

    @native("<init>", "(Lnet/minecraft/potion/Effect;ILnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, effect, level, properties):
        pass


class TallFlowerBlock(Block):
    NAME = "net/minecraft/block/TallFlowerBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class DoublePlantBlock(Block):
    NAME = "net/minecraft/block/DoublePlantBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_176492_b": None
        })

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class VineBlock(Block):
    NAME = "net/minecraft/block/VineBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class BushBlock(Block):
    NAME = "net/minecraft/block/BushBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class IWaterLoggable(NativeClass):
    NAME = "net/minecraft/block/IWaterLoggable"


class HorizontalBlock(Block):
    NAME = "net/minecraft/block/HorizontalBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_185512_D": None,
        })


class SixWayBlock(Block):
    NAME = "net/minecraft/block/SixWayBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_196488_a": None,
            "field_196490_b": None,
            "field_196492_c": None,
            "field_196495_y": None,
            "field_196496_z": None,
            "field_196489_A": None,
        })

    @native("<init>", "(FLnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, value, properties):
        pass

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass


class MushroomBlock(Block):
    NAME = "net/minecraft/block/MushroomBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        pass


class FlowerPotBlock(Block):
    NAME = "net/minecraft/block/FlowerPotBlock"

    @native("<init>", "(Lnet/minecraft/block/Block;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, block, properties):
        pass


class IPlantable(NativeClass):
    NAME = "net/minecraftforge/common/IPlantable"


class IGrowable(NativeClass):
    NAME = "net/minecraft/block/IGrowable"


class Item_Properties(NativeClass):
    NAME = "net/minecraft/item/Item$Properties"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("func_200916_a", "(Lnet/minecraft/item/ItemGroup;)Lnet/minecraft/item/Item$Properties;")
    def setItemGroup(self, instance, item_group):
        return instance


class ItemGroup(NativeClass):
    NAME = "net/minecraft/item/ItemGroup"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_78ß32_a": None,
            "field_78032_a": [],
        })

    @native("<init>", "(ILjava/lang/String;)V")
    def init(self, instance, a: int, b: str):
        pass


class BlockItem(NativeClass):
    NAME = "net/minecraft/item/BlockItem"

    @native("<init>", "(Lnet/minecraft/block/Block;Lnet/minecraft/item/Item$Properties;)V")
    def init(self, instance, block, properties):
        pass

    @native("setRegistryName", "(Ljava/lang/String;)Lnet/minecraftforge/registries/IForgeRegistryEntry;")
    def setRegistryName(self, instance, name: str):
        return instance


class AxeItem(NativeClass):
    NAME = "net/minecraft/item/AxeItem"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "field_203176_a": {}
        }


class HoeItem(NativeClass):
    NAME = "net/minecraft/item/HoeItem"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "field_195973_b": {},
        }


class ShovelItem(NativeClass):
    NAME = "net/minecraft/item/ShovelItem"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "field_195955_e": {}
        }


class IItemProvider(NativeClass):
    NAME = "net/minecraft/util/IItemProvider"

    @native("func_199767_j", "()Lnet/minecraft/item/Item;")
    def getItem(self, instance):
        pass


class AttachFace(NativeClass):
    NAME = "net/minecraft/state/properties/AttachFace"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "FLOOR": "net/minecraft/state/properties/AttachFace::FLOOR"
        })


class BlockState(NativeClass):
    NAME = "net/minecraft/block/BlockState"

    @native("func_206870_a", "(Lnet/minecraft/state/Property;Ljava/lang/Comparable;)Ljava/lang/Object;")
    def func_206870_a(self, instance, prop, value):
        pass


class BlockStateProperties(NativeClass):
    NAME = "net/minecraft/state/properties/BlockStateProperties"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_208137_al": None,
            "field_208198_y": None,
        })


class DoubleBlockHalf(NativeClass):
    NAME = "net/minecraft/state/properties/DoubleBlockHalf"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "LOWER": "net/minecraft/state/properties/DoubleBlockHalf::UPPER"
        })


class Direction(NativeClass):
    NAME = "net/minecraft/util/Direction"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "NORTH": "net/minecraft/util/Direction::NORTH",
            "SOUTH": "net/minecraft/util/Direction::SOUTH",
            "WEST": "net/minecraft/util/Direction::WEST",
            "EAST": "net/minecraft/util/Direction::EAST",
        })


class Tree(NativeClass):
    NAME = "net/minecraft/block/trees/Tree"

    @native("<init>", "()V")
    def init(self, instance):
        pass


class BigTree(NativeClass):
    NAME = "net/minecraft/block/trees/BigTree"

    @native("<init>", "()V")
    def init(self, instance):
        pass

