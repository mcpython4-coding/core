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
from mcpython.loader.java.Java import NativeClass, native


class NetworkRegistry(NativeClass):
    NAME = "net/minecraftforge/fml/network/NetworkRegistry"

    @native(
        "newSimpleChannel",
        "(Lnet/minecraft/util/ResourceLocation;Ljava/util/function/Supplier;Ljava/util/function/Predicate;Ljava/util/function/Predicate;)Lnet/minecraftforge/fml/network/simple/SimpleChannel;",
    )
    def newSimpleChannel(self, namespapce, supplier, predicate1, predicate2):
        return self.vm.get_class(
            "net/minecraftforge/fml/network/simple/SimpleChannel",
            version=self.internal_version,
        ).create_instance()


class SimpleChannel(NativeClass):
    NAME = "net/minecraftforge/fml/network/simple/SimpleChannel"

    @native(
        "registerMessage",
        "(ILjava/lang/Class;Ljava/util/function/BiConsumer;Ljava/util/function/Function;Ljava/util/function/BiConsumer;)Lnet/minecraftforge/fml/network/simple/IndexedMessageCodec$MessageHandler;",
    )
    def registerMessage(self, instance, id, cls, consumer_1, function, consumer_2):
        pass


class NetworkRegistry__ChannelBuilder(NativeClass):
    NAME = "net/minecraftforge/fml/network/NetworkRegistry$ChannelBuilder"

    @native(
        "named",
        "(Lnet/minecraft/util/ResourceLocation;)Lnet/minecraftforge/fml/network/NetworkRegistry$ChannelBuilder;",
    )
    def named(self, name):
        return self.create_instance()

    @native(
        "clientAcceptedVersions",
        "(Ljava/util/function/Predicate;)Lnet/minecraftforge/fml/network/NetworkRegistry$ChannelBuilder;",
    )
    def clientAcceptedVersions(self, instance, predicate):
        return instance

    @native(
        "serverAcceptedVersions",
        "(Ljava/util/function/Predicate;)Lnet/minecraftforge/fml/network/NetworkRegistry$ChannelBuilder;",
    )
    def serverAcceptedVersions(self, instance, predicate):
        return instance

    @native(
        "networkProtocolVersion",
        "(Ljava/util/function/Supplier;)Lnet/minecraftforge/fml/network/NetworkRegistry$ChannelBuilder;",
    )
    def networkProtocolVersion(self, instance, supplier):
        return instance

    @native("simpleChannel", "()Lnet/minecraftforge/fml/network/simple/SimpleChannel;")
    def simpleChannel(self, instance):
        return self.vm.get_class(
            "net/minecraftforge/fml/network/simple/SimpleChannel",
            version=self.internal_version,
        )

    @native(
        "eventNetworkChannel",
        "()Lnet/minecraftforge/fml/network/event/EventNetworkChannel;",
    )
    def eventNetworkChannel(self, instance):
        return self.vm.get_class(
            "net/minecraftforge/fml/event/EventNetworkChannel",
            version=self.internal_version,
        )


class EventNetworkChannel(NativeClass):
    NAME = "net/minecraftforge/fml/network/event/EventNetworkChannel"

    @native("registerObject", "(Ljava/lang/Object;)V")
    def registerObject(self, instance, obj):
        pass
