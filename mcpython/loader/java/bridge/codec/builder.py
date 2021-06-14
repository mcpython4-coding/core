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


class RecordCodecBuilder(NativeClass):
    NAME = "com/mojang/serialization/codecs/RecordCodecBuilder"

    @native("create", "(Ljava/util/function/Function;)Lcom/mojang/serialization/Codec;")
    def create(self, method):
        pass


class Codec(NativeClass):
    NAME = "com/mojang/serialization/Codec"

    @native("fieldOf", "(Ljava/lang/String;)Lcom/mojang/serialization/MapCodec;")
    def fieldOf(self, instance, name: str):
        return self.vm.get_class("com/mojang/serialization/MapCodec", version=self.internal_version).create_instance()

    @native("listOf", "()Lcom/mojang/serialization/Codec;")
    def listOf(self, instance):
        return instance

    @native("pair",
            "(Lcom/mojang/serialization/Codec;Lcom/mojang/serialization/Codec;)Lcom/mojang/serialization/Codec;")
    def pair(self, instance, a, b):
        return instance

    @native("unboundedMap",
            "(Lcom/mojang/serialization/Codec;Lcom/mojang/serialization/Codec;)Lcom/mojang/serialization/codecs/UnboundedMapCodec;")
    def unboundedMap(self, instance, codec_key, codec_value):
        return self.vm.get_class("com/mojang/serialization/codecs/UnboundedMapCodec", version=self.internal_version).create_instance()


class MapCodec(Codec):
    NAME = "com/mojang/serialization/MapCodec"

    @native("codec", "()Lcom/mojang/serialization/Codec;")
    def codec(self, instance):
        return instance


class UnboundedMapCodec(Codec):
    NAME = "com/mojang/serialization/codecs/UnboundedMapCodec"
