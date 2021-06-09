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


class ResourceLocation(NativeClass):
    NAME = "net/minecraft/util/ResourceLocation"

    def create_instance(self):
        instance = super().create_instance()
        instance.name = ""
        return instance

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, location: str):
        instance.name = location

    @native("<init>", "(Ljava/lang/String;Ljava/lang/String;)V")
    def init2(self, instance, namespace: str, postfix: str):
        instance.name = namespace + ":" + postfix

    @native("toString", "()Ljava/lang/String;")
    def toString(self, instance):
        return instance if isinstance(instance, str) else instance.name


class IBooleanFunction(NativeClass):
    NAME = "net/minecraft/util/math/shapes/IBooleanFunction"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "field_223234_e_": None,
            }
        )


class VoxelShape(NativeClass):
    NAME = "net/minecraft/util/math/shapes/VoxelShape"


class VoxelShapes(NativeClass):
    NAME = "net/minecraft/util/math/shapes/VoxelShapes"

    @native(
        "func_197878_a",
        "(Lnet/minecraft/util/math/shapes/VoxelShape;Lnet/minecraft/util/math/shapes/VoxelShape;Lnet/minecraft/util/math/shapes/IBooleanFunction;)Lnet/minecraft/util/math/shapes/VoxelShape;",
    )
    def func_197878_a(self, a, b, function):
        return self.vm.get_class(
            "net/minecraft/util/math/shapes/VoxelShape", version=self.internal_version
        ).create_instance()


class AxisAlignedBB(NativeClass):
    NAME = "net/minecraft/util/math/AxisAlignedBB"

    @native("<init>", "(DDDDDD)V")
    def init(self, instance, a, b, c, d, e, f):
        pass


class IStringSerializable(NativeClass):
    NAME = "net/minecraft/util/IStringSerializable"


class LazyValue(NativeClass):
    NAME = "net/minecraft/util/LazyValue"

    @native("<init>", "(Ljava/util/function/Supplier;)V")
    def init(self, instance, supplier):
        instance.supplier = supplier

    @native("func_179281_c", "()Ljava/lang/Object;")
    def get(self, instance):
        return instance.supplier.invoke()


class Lazy(NativeClass):
    NAME = "net/minecraftforge/common/util/Lazy"

    @native("concurrentOf", "(Ljava/util/function/Supplier;)Lnet/minecraftforge/common/util/Lazy;")
    def concurrentOf(self, supplier):
        return self.create_instance()

    @native("get", "()Ljava/lang/Object;")
    def get(self, instance):
        pass
