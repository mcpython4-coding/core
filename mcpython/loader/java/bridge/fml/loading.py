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


class FMLLoadingContext(NativeClass):
    NAME = "net/minecraftforge/fml/javafmlmod/FMLJavaModLoadingContext"

    @native("get", "()Lnet/minecraftforge/fml/javafmlmod/FMLJavaModLoadingContext;")
    def get_context(self):
        pass

    @native("getModEventBus", "()Lnet/minecraftforge/eventbus/api/IEventBus;")
    def getModEventBus(self, instance):
        pass


class ModLoadingContext(NativeClass):
    NAME = "net/minecraftforge/fml/ModLoadingContext"

    @native("get", "()Lnet/minecraftforge/fml/ModLoadingContext;")
    def get_context(self):
        pass

    @native("registerConfig", "(Lnet/minecraftforge/fml/config/ModConfig$Type;Lnet/minecraftforge/common/ForgeConfigSpec;Ljava/lang/String;)V")
    def registerConfig(self, instance, config_type, config_spec, file_name: str):
        pass


class EventBus(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/IEventBus"

    @native("addListener", "(Ljava/util/function/Consumer;)V")
    def addListener(self, instance, function):
        pass


class DistMarker(NativeClass):
    NAME = "net/minecraftforge/api/distmarker/Dist"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"CLIENT": "client", "SERVER": "server"})


class FMLEnvironment(NativeClass):
    NAME = "net/minecraftforge/fml/loading/FMLEnvironment"

    def __init__(self):
        super().__init__()
        self.exposed_attributes["dist"] = "client" if shared.IS_CLIENT else "server"


class DistExecutor(NativeClass):
    NAME = "net/minecraftforge/fml/DistExecutor"

    @native(
        "runForDist",
        "(Ljava/util/function/Supplier;Ljava/util/function/Supplier;)Ljava/lang/Object;",
    )
    def runForDist(self, left, right):
        pass


class FMLPaths(NativeClass):
    NAME = "net/minecraftforge/fml/loading/FMLPaths"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {"CONFIGDIR": None}

    @native("get", "()Ljava/nio/file/Path;")
    def get(self, instance):
        return None


class ModConfig_Type(NativeClass):
    NAME = "net/minecraftforge/fml/config/ModConfig$Type"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {"COMMON": None, "CLIENT": None}


class ForgeConfigSpec_Builder(NativeClass):
    NAME = "net/minecraftforge/common/ForgeConfigSpec$Builder"

    @native('<init>', '()V')
    def init(self, instance):
        pass

    @native("comment", "(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;")
    def comment(self, instance, text: str):
        return instance

    @native('push', '(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;')
    def push(self, instance, text: str):
        return instance

    @native("defineEnum", "(Ljava/lang/String;Ljava/lang/Enum;)Lnet/minecraftforge/common/ForgeConfigSpec$EnumValue;")
    def defineEnum(self, instance, name: str, enum):
        return instance

    @native("define", "(Ljava/lang/String;Z)Lnet/minecraftforge/common/ForgeConfigSpec$BooleanValue;")
    def defineBool(self, instance, name: str, default: bool):
        return instance

    @native("pop", "()Lnet/minecraftforge/common/ForgeConfigSpec$Builder;")
    def pop(self, instance):
        return instance

    @native("build", "()Lnet/minecraftforge/common/ForgeConfigSpec;")
    def build(self, instance):
        return
