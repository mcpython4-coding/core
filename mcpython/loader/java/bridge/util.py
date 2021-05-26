from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class ResourceLocation(NativeClass):
    NAME = "net/minecraft/util/ResourceLocation"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, location: str):
        pass
