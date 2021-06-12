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


class CommentedFileConfig(NativeClass):
    NAME = "com/electronwill/nightconfig/core/file/CommentedFileConfig"

    @native(
        "builder",
        "(Ljava/nio/file/Path;)Lcom/electronwill/nightconfig/core/file/CommentedFileConfigBuilder;",
    )
    def builder(self, path):
        return self.vm.get_class(
            "com/electronwill/nightconfig/core/file/CommentedFileConfigBuilder",
            version=self.internal_version,
        ).create_instance()

    @native("load", "()V")
    def load(self, instance):
        pass


class CommentedFileConfigBuilder(NativeClass):
    NAME = "com/electronwill/nightconfig/core/file/CommentedFileConfigBuilder"

    @native("sync", "()Lcom/electronwill/nightconfig/core/file/GenericBuilder;")
    def sync(self, instance):
        return self.vm.get_class(
            "com/electronwill/nightconfig/core/file/GenericBuilder",
            version=self.internal_version,
        ).create_instance()

    @native("load", "()V")
    def load(self, instance):
        pass


class GenericBuilder(NativeClass):
    NAME = "com/electronwill/nightconfig/core/file/GenericBuilder"

    @native("autosave", "()Lcom/electronwill/nightconfig/core/file/GenericBuilder;")
    def autosave(self, instance):
        return instance

    @native(
        "writingMode",
        "(Lcom/electronwill/nightconfig/core/io/WritingMode;)Lcom/electronwill/nightconfig/core/file/GenericBuilder;",
    )
    def writingMode(self, instance, mode):
        return instance

    @native("build", "()Lcom/electronwill/nightconfig/core/file/FileConfig;")
    def build(self, *_):
        return self.vm.get_class(
            "com/electronwill/nightconfig/core/file/CommentedFileConfigBuilder",
            version=self.internal_version,
        ).create_instance()


class WritingMode(NativeClass):
    NAME = "com/electronwill/nightconfig/core/io/WritingMode"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "REPLACE": 0,
            }
        )
