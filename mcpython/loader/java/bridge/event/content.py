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
        # todo: this seems odd
        instance = self.vm.get_class("net/minecraft/block/RotatedPillarBlock", version=self.internal_version).create_instance()
        instance.properties = self.vm.get_class("net/minecraft/block/AbstractBlock$Properties", version=self.internal_version).create_instance()
        return instance


class AbstractBlock(NativeClass):
    NAME = "net/minecraft/block/AbstractBlock"


class AbstractBlock_Properties(NativeClass):
    NAME = "net/minecraft/block/AbstractBlock$Properties"

    def create_instance(self):
        instance = super().create_instance()
        instance.hardness = instance.blast_resistance = 0
        instance.harvest_level = 0
        instance.harvest_tool = 0
        return instance

    @native("func_200949_a", "(Lnet/minecraft/block/material/Material;Lnet/minecraft/block/material/MaterialColor;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200949_a(self, material, material_color):
        return self.create_instance()

    @native("func_200943_b", "(F)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200943_b(self, instance, value):
        instance.hardness = instance.blast_resistance = value
        return instance

    @native("func_200947_a", "(Lnet/minecraft/block/SoundType;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def setSoundType(self, instance, sound_type):
        return instance

    @native("harvestLevel", "(I)Lnet/minecraft/block/AbstractBlock$Properties;")
    def harvestLevel(self, instance, level: int):
        instance.harvest_level = level
        return instance

    @native("harvestTool", "(Lnet/minecraftforge/common/ToolType;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def harvestTool(self, instance, tool):
        # todo: inject into TAG
        instance.harvest_tool = tool
        return instance

    @native("func_200950", "(Lnet/minecraft/block/AbstractBlock;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200950(self, instance, a):
        return instance

    @native("func_200950_a", "(Lnet/minecraft/block/AbstractBlock;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200950_a(self, instance):
        return instance.properties

    @native("func_200948_a", "(FF)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_200948_a(self, instance, a, b):
        instance.hardness = instance.blast_resistance = a, b
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

    @native("func_235842_b_", "(Lnet/minecraft/block/AbstractBlock$IPositionPredicate;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_235842_b_(self, instance, position_predicate):
        return instance

    @native("func_235828_a_", "(Lnet/minecraft/block/AbstractBlock$IPositionPredicate;)Lnet/minecraft/block/AbstractBlock$Properties;")
    def func_235828_a_(self, instance, position_predicate):
        return instance


class SoundType(NativeClass):
    NAME = "net/minecraft/block/SoundType"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_185855_h": None,
            "field_185850_c": None,
            "field_185848_a": None,
            "field_185851_d": None,
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
        instance.properties = properties

    @native("func_176223_P", "()Lnet/minecraft/block/BlockState;")
    def func_176223_P(self, instance):
        return instance.properties

    @native("setRegistryName", "(Ljava/lang/String;)Lnet/minecraftforge/registries/IForgeRegistryEntry;")
    def setRegistryName(self, instance, name: str):
        instance.registry_name = name
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
        instance.properties = properties


class StairsBlock(Block):
    NAME = "net/minecraft/block/StairsBlock"

    @native("<init>", "(Lnet/minecraft/block/BlockState;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, a, properties):
        instance.properties = properties


class SlabBlock(Block):
    NAME = "net/minecraft/block/SlabBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class WallBlock(Block):
    NAME = "net/minecraft/block/WallBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class GrassBlock(Block):
    NAME = "net/minecraft/block/GrassBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


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
        instance.properties = properties

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class HugeMushroomBlock(Block):
    NAME = "net/minecraft/block/HugeMushroomBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class SaplingBlock(Block):
    NAME = "net/minecraft/block/SaplingBlock"

    @native("<init>", "(Lnet/minecraft/block/trees/Tree;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, tree, properties):
        instance.properties = properties

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, block_state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class LeavesBlock(Block):
    NAME = "net/minecraft/block/LeavesBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class RotatedPillarBlock(Block):
    NAME = "net/minecraft/block/RotatedPillarBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class FenceBlock(Block):
    NAME = "net/minecraft/block/FenceBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class FenceGateBlock(Block):
    NAME = "net/minecraft/block/FenceGateBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class DoorBlock(Block):
    NAME = "net/minecraft/block/DoorBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class TrapDoorBlock(Block):
    NAME = "net/minecraft/block/TrapDoorBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class PressurePlateBlock(Block):
    NAME = "net/minecraft/block/PressurePlateBlock"

    @native("<init>", "(Lnet/minecraft/block/PressurePlateBlock$Sensitivity;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, sensitivity, properties):
        instance.properties = properties


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
        instance.properties = properties


class FlowerBlock(Block):
    NAME = "net/minecraft/block/FlowerBlock"

    @native("<init>", "(Lnet/minecraft/potion/Effect;ILnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, effect, level, properties):
        instance.properties = properties


class TallFlowerBlock(Block):
    NAME = "net/minecraft/block/TallFlowerBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class DoublePlantBlock(Block):
    NAME = "net/minecraft/block/DoublePlantBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_176492_b": None
        })

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    def get_dynamic_field_keys(self):
        return super().get_dynamic_field_keys() | {"field_176227_L"}


class VineBlock(Block):
    NAME = "net/minecraft/block/VineBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class BushBlock(Block):
    NAME = "net/minecraft/block/BushBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class IWaterLoggable(NativeClass):
    NAME = "net/minecraft/block/IWaterLoggable"


class HorizontalBlock(Block):
    NAME = "net/minecraft/block/HorizontalBlock"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_185512_D": None,
        })

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass

    @native("func_176223_P", "()Lnet/minecraft/block/BlockState;")
    def func_176223_P(self, instance):
        return instance


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
        instance.properties = properties

    @native("func_180632_j", "(Lnet/minecraft/block/BlockState;)V")
    def func_180632_j(self, instance, state):
        pass


class MushroomBlock(Block):
    NAME = "net/minecraft/block/MushroomBlock"

    @native("<init>", "(Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties


class FlowerPotBlock(Block):
    NAME = "net/minecraft/block/FlowerPotBlock"

    @native("<init>", "(Lnet/minecraft/block/Block;Lnet/minecraft/block/AbstractBlock$Properties;)V")
    def init(self, instance, block, properties):
        instance.properties = properties


class IPlantable(NativeClass):
    NAME = "net/minecraftforge/common/IPlantable"


class IGrowable(NativeClass):
    NAME = "net/minecraft/block/IGrowable"


class Item(NativeClass):
    NAME = "net/minecraft/item/Item"

    def create_instance(self):
        instance = super().create_instance()
        instance.properties = None
        instance.registry_name = None
        return instance

    @native("<init>", "(Lnet/minecraft/item/Item$Properties;)V")
    def init(self, instance, properties):
        instance.properties = properties

    @native("setRegistryName", "(Ljava/lang/String;)Lnet/minecraftforge/registries/IForgeRegistryEntry;")
    def setRegistryName(self, instance, name):
        instance.registry_name = name
        return instance

    @native("func_70067_L", "()Z")
    def func_70067_L(self, instance):
        return 0


class Item_Properties(NativeClass):
    NAME = "net/minecraft/item/Item$Properties"

    def create_instance(self):
        instance = super().create_instance()
        instance.item_group = None
        instance.rarity = None
        return instance

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("func_200916_a", "(Lnet/minecraft/item/ItemGroup;)Lnet/minecraft/item/Item$Properties;")
    def setItemGroup(self, instance, item_group):
        instance.item_group = item_group
        return instance

    @native("func_208103_a", "(Lnet/minecraft/item/Rarity;)Lnet/minecraft/item/Item$Properties;")
    def setRarity(self, instance, rarity):
        instance.rarity = rarity
        return instance

    @native("func_200917_a", "(I)Lnet/minecraft/item/Item$Properties;")
    def func_200917_a(self, instance, value):
        return instance


class ItemGroup(NativeClass):
    NAME = "net/minecraft/item/ItemGroup"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            # Exposed for a ID of the tab, as mc requires it for no reason. We don't need it
            "field_78032_a": []
        })

    @native("<init>", "(ILjava/lang/String;)V")
    def init(self, instance, a: int, b: str):
        import mcpython.client.gui.InventoryCreativeTab

        import mcpython.loader.java.Runtime
        runtime = mcpython.loader.java.Runtime.Runtime()

        # create the item stack
        stack = runtime.run_method(instance.get_class().get_method("func_78016_d", "()Lnet/minecraft/item/ItemStack;"))

        instance.underlying_tab = mcpython.client.gui.InventoryCreativeTab.CreativeItemTab(b, stack.underlying_stack)

        @shared.mod_loader("minecraft", "stage:item_groups:load")
        def add_tab():
            mcpython.client.gui.InventoryCreativeTab.CT_MANAGER.add_tab(instance.underlying_tab)


class ItemStack(NativeClass):
    NAME = "net/minecraft/item/ItemStack"

    @native("<init>", "(Lnet/minecraft/util/IItemProvider;)V")
    def init(self, instance, item_provider):
        import mcpython.common.container.ResourceStack
        instance.underlying_stack = mcpython.common.container.ResourceStack.ItemStack()


class BlockItem(Item):
    NAME = "net/minecraft/item/BlockItem"

    @native("<init>", "(Lnet/minecraft/block/Block;Lnet/minecraft/item/Item$Properties;)V")
    def init(self, instance, block, properties):
        instance.block = block
        instance.properties = properties

    @native("setRegistryName", "(Ljava/lang/String;)Lnet/minecraftforge/registries/IForgeRegistryEntry;")
    def setRegistryName(self, instance, name: str):
        instance.registry_name = name
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


class MusicDiscItem(Item):
    NAME = "net/minecraft/item/MusicDiscItem"

    @native("<init>", "(ILjava/util/function/Supplier;Lnet/minecraft/item/Item$Properties;)V")
    def init(self, instance, value, supplier, properties):
        instance.properties = properties


class IItemProvider(NativeClass):
    NAME = "net/minecraft/util/IItemProvider"

    @native("func_199767_j", "()Lnet/minecraft/item/Item;")
    def getItem(self, instance):
        pass


class ItemRarity(NativeClass):
    NAME = "net/minecraft/item/Rarity"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "RARE": "net/minecraft/item/Rarity::RARE"
        })


class AttachFace(NativeClass):
    NAME = "net/minecraft/state/properties/AttachFace"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "FLOOR": "net/minecraft/state/properties/AttachFace::FLOOR",
            "WALL": "net/minecraft/state/properties/AttachFace::WALL",
            "CEILING": "net/minecraft/state/properties/AttachFace::CEILING"
        })

    @native("values", "()[Lnet/minecraft/state/properties/AttachFace;")
    def values(self):
        return list(self.exposed_attributes.keys())

    @native("ordinal", "()I")
    def ordinal(self, instance):
        return 0


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

    @native("values", "()[Lnet/minecraft/util/Direction;")
    def values(self):
        return list(self.exposed_attributes.values())

    @native("ordinal", "()I")
    def ordinal(self, instance):
        return 0


class EnumProperty(NativeClass):
    NAME = "net/minecraft/state/EnumProperty"

    @native("func_177709_a", "(Ljava/lang/String;Ljava/lang/Class;)Lnet/minecraft/state/EnumProperty;")
    def func_1777709_a(self, name, cls):
        return self.create_instance()


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


class EntityPredicates(NativeClass):
    NAME = "net/minecraft/util/EntityPredicates"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "field_180132_d": None,
        })

