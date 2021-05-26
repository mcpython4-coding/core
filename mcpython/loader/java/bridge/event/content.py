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


class Block(NativeClass):
    NAME = "net/minecraft/block/Block"

    @native("func_176223_P", "()Lnet/minecraft/block/BlockState;")
    def func_176223_P(self, instance):
        pass


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

