from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class ForgeWorldType(NativeClass):
    NAME = "net/minecraftforge/common/world/ForgeWorldType"

    @native(
        "<init>",
        "(Lnet/minecraftforge/common/world/ForgeWorldType$IBasicChunkGeneratorFactory;)V",
    )
    def init(self, instance, factory):
        instance.registry_name = None

    @native(
        "setRegistryName",
        "(Lnet/minecraft/util/ResourceLocation;)Lnet/minecraftforge/registries/IForgeRegistryEntry;",
    )
    def setRegistryName(self, instance, name):
        instance.registry_name = name
