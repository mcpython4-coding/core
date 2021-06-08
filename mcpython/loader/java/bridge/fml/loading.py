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
import traceback

import mcpython.common.mod.ModLoader
from mcpython import logger, shared
from mcpython.loader.java.Java import NativeClass, native
from mcpython.loader.java.Runtime import Runtime, UnhandledInstructionException
from mcpython.loader.java.JavaExceptionStack import StackCollectingException


class Mod(NativeClass):
    NAME = "net/minecraftforge/fml/common/Mod"

    def on_annotate(self, cls, args):
        import mcpython.loader.java.Runtime

        runtime = mcpython.loader.java.Runtime.Runtime()
        instance = cls.create_instance()
        runtime.run_method(cls.get_method("<init>", "()V"), instance)


class Mod_EventBusSubscriber(NativeClass):
    NAME = "net/minecraftforge/fml/common/Mod$EventBusSubscriber"

    def on_annotate(self, cls, args):

        if (
            "registerBlocks",
            "(Lnet/minecraftforge/event/RegistryEvent$Register;)V",
        ) in cls.methods:
            current_mod = shared.CURRENT_EVENT_SUB

            @shared.mod_loader("minecraft", "stage:block:factory_usage")
            def load():
                shared.CURRENT_EVENT_SUB = current_mod
                method = cls.get_method(
                    "registerBlocks",
                    "(Lnet/minecraftforge/event/RegistryEvent$Register;)V",
                )

                runtime = Runtime()

                try:
                    runtime.run_method(
                        method, shared.registry.get_by_name("minecraft:block")
                    )
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(e.format_exception())
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(traceback.format_exc())
                    traceback.print_exc()
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        if (
            "registerItems",
            "(Lnet/minecraftforge/event/RegistryEvent$Register;)V",
        ) in cls.methods:
            current_mod = shared.CURRENT_EVENT_SUB

            @shared.mod_loader("minecraft", "stage:item:factory_usage")
            def load():
                shared.CURRENT_EVENT_SUB = current_mod
                method = cls.get_method(
                    "registerItems",
                    "(Lnet/minecraftforge/event/RegistryEvent$Register;)V",
                )

                runtime = Runtime()

                try:
                    runtime.run_method(
                        method, shared.registry.get_by_name("minecraft:item")
                    )
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(e.format_exception())
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(traceback.format_exc())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        # else:
        # print("sub", 2, cls, args)


class Mod_EventBusSubscriber_Bus(NativeClass):
    NAME = "net/minecraftforge/fml/common/Mod$EventBusSubscriber$Bus"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "MOD": "net/minecraftforge/fml/common/Mod$EventBusSubscriber$Bus::MOD",
                "FORGE": "net/minecraftforge/fml/common/Mod$EventBusSubscriber$Bus::FORGE",
            }
        )


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

    @native(
        "registerConfig",
        "(Lnet/minecraftforge/fml/config/ModConfig$Type;Lnet/minecraftforge/common/ForgeConfigSpec;Ljava/lang/String;)V",
    )
    def registerConfig(self, instance, config_type, config_spec, file_name: str):
        pass

    @native(
        "registerConfig",
        "(Lnet/minecraftforge/fml/config/ModConfig$Type;Lnet/minecraftforge/common/ForgeConfigSpec;)V",
    )
    def registerConfig2(self, instance, config_type, config_spec):
        pass


class EventBus(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/IEventBus"

    @native("addListener", "(Ljava/util/function/Consumer;)V")
    def addListener(self, instance, function):
        if function.name == "commonSetup":
            runtime = Runtime()
            try:
                runtime.run_method(function, None)
            except StackCollectingException as e:
                import mcpython.client.state.StateLoadingException
                mcpython.client.state.StateLoadingException.error_occur(e.format_exception())
                print(e.format_exception())
                raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
            except UnhandledInstructionException:
                logger.print_exception(
                    f"during invoking commonSetup listener {function}"
                )

                if shared.IS_CLIENT:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )

                    import mcpython.common.mod.ModLoader

                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(traceback.format_exc())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        elif function.name == "clientSetup":
            if shared.IS_CLIENT:
                runtime = Runtime()
                try:
                    runtime.run_method(function, None)
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(e.format_exception())
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except UnhandledInstructionException:
                    logger.print_exception(
                        f"during invoking clientSetup listener {function}"
                    )

                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )

                    import mcpython.common.mod.ModLoader

                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(traceback.format_exc())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        elif function.name == "loadComplete":

            def run():
                runtime = Runtime()
                try:
                    runtime.run_method(function, None)
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException
                    mcpython.client.state.StateLoadingException.error_occur(e.format_exception())
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except UnhandledInstructionException:
                    logger.print_exception(
                        f"during invoking loadComplete listener {function}"
                    )

                    if shared.IS_CLIENT:
                        import mcpython.client.state.StateLoadingException

                        mcpython.client.state.StateLoadingException.error_occur(
                            traceback.format_exc()
                        )

                        import mcpython.common.mod.ModLoader

                        import mcpython.client.state.StateLoadingException
                        mcpython.client.state.StateLoadingException.error_occur(traceback.format_exc())
                        raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

            shared.mod_loader("minecraft", "stage:post")(run)

        else:
            print("missing BRIDGE binding for", function)

    @native("register", "(Ljava/lang/Object;)V")
    def register(self, instance, obj):
        pass


class DistMarker(NativeClass):
    NAME = "net/minecraftforge/api/distmarker/Dist"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"CLIENT": "client", "SERVER": "server"})

    @native("isClient", "()Z")
    def isClient(self, instance):
        return int(instance == "client")


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
        pass  # todo: run code when on the respective side

    @native(
        "unsafeRunForDist",
        "(Ljava/util/function/Supplier;Ljava/util/function/Supplier;)Ljava/lang/Object;",
    )
    def unsafeRunForDist(self, left, right):
        return self.runForDist(left, right)


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


class ForgeConfigSpec__Builder(NativeClass):
    NAME = "net/minecraftforge/common/ForgeConfigSpec$Builder"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native(
        "comment",
        "(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;",
    )
    def comment(self, instance, text: str):
        return instance

    @native(
        "push",
        "(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;",
    )
    def push(self, instance, text: str):
        return instance

    @native(
        "defineEnum",
        "(Ljava/lang/String;Ljava/lang/Enum;)Lnet/minecraftforge/common/ForgeConfigSpec$EnumValue;",
    )
    def defineEnum(self, instance, name: str, enum):
        return instance

    @native(
        "define",
        "(Ljava/lang/String;Z)Lnet/minecraftforge/common/ForgeConfigSpec$BooleanValue;",
    )
    def defineBool(self, instance, name: str, default: bool):
        return instance

    @native("pop", "()Lnet/minecraftforge/common/ForgeConfigSpec$Builder;")
    def pop(self, instance):
        return instance

    @native("build", "()Lnet/minecraftforge/common/ForgeConfigSpec;")
    def build(self, instance):
        return

    @native(
        "configure",
        "(Ljava/util/function/Function;)Lorg/apache/commons/lang3/tuple/Pair;",
    )
    def configure(self, instance, function):
        return None, None

    @native(
        "comment",
        "([Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;",
    )
    def comment(self, instance, comments):
        return instance

    @native(
        "comment",
        "(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;",
    )
    def comment2(self, instance, comments):
        return instance

    @native(
        "define",
        "(Ljava/lang/String;Ljava/lang/Object;)Lnet/minecraftforge/common/ForgeConfigSpec$ConfigValue;",
    )
    def define(self, instance, name, obj):
        return instance

    @native(
        "defineInRange",
        "(Ljava/lang/String;III)Lnet/minecraftforge/common/ForgeConfigSpec$IntValue;",
    )
    def defineInRange(self, instance, name, a, b, c):
        return instance

    @native(
        "defineList",
        "(Ljava/lang/String;Ljava/util/List;Ljava/util/function/Predicate;)Lnet/minecraftforge/common/ForgeConfigSpec$ConfigValue;",
    )
    def defineList(self, instance, name, a, b):
        return instance


class FMLCommonSetupEvent(NativeClass):
    NAME = "net/minecraftforge/fml/event/lifecycle/FMLCommonSetupEvent"

    @native(
        "enqueueWork", "(Ljava/lang/Runnable;)Ljava/util/concurrent/CompletableFuture;"
    )
    def enqueueWork(self, instance, work):
        # todo: make run safe
        import mcpython.loader.java.Runtime

        runtime = mcpython.loader.java.Runtime.Runtime()
        runtime.run_method(work, None)


class OnlyIn(NativeClass):
    NAME = "net/minecraftforge/api/distmarker/OnlyIn"

    def on_annotate(self, cls, args):
        logger.println(
            f"[FML][WARN] got internal @OnlyIn marker on cls {cls.name} not specified for use in mods. Things may break!"
        )


class MinecraftForge(NativeClass):
    NAME = "net/minecraftforge/common/MinecraftForge"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "EVENT_BUS": None,
            }
        )
