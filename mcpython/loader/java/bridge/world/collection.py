from mcpython.loader.java.Java import native, NativeClass
from mcpython import shared


class ForgeWorldType(NativeClass):
    NAME = "net/minecraftforge/common/world/ForgeWorldType"

    @native("<init>", "(Lnet/minecraftforge/common/world/ForgeWorldType$IBasicChunkGeneratorFactory;)V")
    def init(self, instance, factory):
        pass

