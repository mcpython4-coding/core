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

    @native("func_110623_a", "()Ljava/lang/String;")
    def getNamespace(self, instance):
        return (
            (instance if isinstance(instance, str) else instance.name).split(":")[0]
            if instance is not None
            else None
        )

    @native("func_110624_b", "()Ljava/lang/String;")
    def func_110624_b(self, instance):
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

    @native(
        "func_197881_a",
        "(Lnet/minecraft/util/math/AxisAlignedBB;)Lnet/minecraft/util/math/shapes/VoxelShape;",
    )
    def func_197881_a(self, *_):
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

    @native(
        "func_233023_a_",
        "(Ljava/util/function/Supplier;Ljava/util/function/Function;)Lcom/mojang/serialization/Codec;",
    )
    def func_233023_a_(self, instance, supplier, function):
        pass


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

    @native(
        "concurrentOf",
        "(Ljava/util/function/Supplier;)Lnet/minecraftforge/common/util/Lazy;",
    )
    def concurrentOf(self, supplier):
        return self.create_instance()

    @native("get", "()Ljava/lang/Object;")
    def get(self, instance):
        pass


class ParametersAreNonnullByDefault(NativeClass):
    NAME = "javax/annotation/ParametersAreNonnullByDefault"

    def on_annotate(self, cls, args):
        pass


class MethodsReturnNonnullByDefault(NativeClass):
    NAME = "mcp/MethodsReturnNonnullByDefault"

    def on_annotate(self, cls, args):
        pass


class DamageSource(NativeClass):
    NAME = "net/minecraft/util/DamageSource"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, v):
        pass

    @native("func_76348_h", "()Lnet/minecraft/util/DamageSource;")
    def func_76348_h(self, instance):
        return instance

    @native("func_151518_m", "()Lnet/minecraft/util/DamageSource;")
    def func_151518_m(self, instance):
        return instance


class NonNullList(NativeClass):
    NAME = "net/minecraft/util/NonNullList"

    @native("func_191196_a", "()Lnet/minecraft/util/NonNullList;")
    def func_191196_a(self):
        return []

    @native("add", "(Ljava/lang/Object;)Z")
    def add(self, instance, entry):
        instance.append(entry)
        return 1


class BlockPos(NativeClass):
    NAME = "net/minecraft/util/math/BlockPos"

    @native("<init>", "(III)V")
    def init(self, instance, x, y, z):
        instance.pos = x, y, z


class SoundEvent(NativeClass):
    NAME = "net/minecraft/util/SoundEvent"


class FolderName(NativeClass):
    NAME = "net/minecraft/world/storage/FolderName"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, name: str):
        pass


class Tuple(NativeClass):
    NAME = "net/minecraft/util/Tuple"

    @native("<init>", "(Ljava/lang/Object;Ljava/lang/Object;)V")
    def init(self, instance, a, b):
        instance.underlying = a, b
