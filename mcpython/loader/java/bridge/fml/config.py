from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class ForgeConfigSpec(NativeClass):
    NAME = "net/minecraftforge/common/ForgeConfigSpec"

    @native("setConfig", "(Lcom/electronwill/nightconfig/core/CommentedConfig;)V")
    def setConfig(self, instance, config_instance):
        pass

