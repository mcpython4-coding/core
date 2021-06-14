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


class BlockTags(NativeClass):
    NAME = "net/minecraft/tags/BlockTags"

    @native("func_199894_a", "(Ljava/lang/String;)Lnet/minecraft/tags/ITag$INamedTag;")
    def getByName(self, name: str):
        return shared.tag_handler.get_tag_for(name, "blocks", or_else_none=True)

    @native("createOptional",
            "(Lnet/minecraft/util/ResourceLocation;)Lnet/minecraftforge/common/Tags$IOptionalNamedTag;")
    def createOptional(self, name: str):
        pass


class ItemTags(NativeClass):
    NAME = "net/minecraft/tags/ItemTags"

    @native("func_199901_a", "(Ljava/lang/String;)Lnet/minecraft/tags/ITag$INamedTag;")
    def func_199901_a(self, name: str):
        return shared.tag_handler.get_tag_for(name, "items", or_else_none=True)


class ForgeTagHandler(NativeClass):
    NAME = "net/minecraftforge/common/ForgeTagHandler"

    @native("createOptionalTag",
            "(Lnet/minecraftforge/registries/IForgeRegistry;Lnet/minecraft/util/ResourceLocation;)Lnet/minecraftforge/common/Tags$IOptionalNamedTag;")
    def createOptionalTag(self, registry, name):
        pass
