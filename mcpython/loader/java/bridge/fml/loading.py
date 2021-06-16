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
from mcpython.loader.java.JavaExceptionStack import StackCollectingException
from mcpython.loader.java.Runtime import Runtime, UnhandledInstructionException


class Minecraft(NativeClass):
    NAME = "net/minecraft/client/Minecraft"

    def __init__(self):
        super().__init__()
        self.instance = self.create_instance()

    @native("func_71410_x", "()Lnet/minecraft/client/Minecraft;", static=True)
    def func_71410_x(self):
        return self.instance

    @native("func_184125_al", "()Lnet/minecraft/client/renderer/color/BlockColors;")
    def func_184125_al(self, instance):
        pass


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

                    mcpython.client.state.StateLoadingException.error_occur(
                        e.format_exception()
                    )
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
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

                    mcpython.client.state.StateLoadingException.error_occur(
                        e.format_exception()
                    )
                    print(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
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

    @native("bus", "()Ljava/util/function/Supplier;")
    def bus(self, instance):
        return lambda: None


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

    @native("registerExtensionPoint", "(Lnet/minecraftforge/fml/ExtensionPoint;Ljava/util/function/Supplier;)V")
    def registerExtensionPoint(self, instance, point, supplier):
        pass

    @native("getActiveContainer", "()Lnet/minecraftforge/fml/ModContainer;")
    def getActiveContainer(self, instance):
        return shared.mod_loader[shared.CURRENT_EVENT_SUB]


class ModContainer(NativeClass):
    NAME = "net/minecraftforge/fml/ModContainer"

    @native("getModId", "()Ljava/lang/String;")
    def getModId(self, instance):
        return instance.name


class EventBus(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/IEventBus"

    @native("addListener", "(Ljava/util/function/Consumer;)V")
    def addListener(self, instance, function):
        func_name = function.name if hasattr(function, "name") else function.native_name

        if func_name == "commonSetup":
            runtime = Runtime()
            try:
                runtime.run_method(function, None)
            except StackCollectingException as e:
                import mcpython.client.state.StateLoadingException

                mcpython.client.state.StateLoadingException.error_occur(
                    e.format_exception()
                )
                logger.print_exception()
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

                    import mcpython.client.state.StateLoadingException
                    import mcpython.common.mod.ModLoader

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        elif func_name == "clientSetup":
            if shared.IS_CLIENT:
                runtime = Runtime()
                try:
                    runtime.run_method(function, None)
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        e.format_exception()
                    )
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

                    import mcpython.client.state.StateLoadingException
                    import mcpython.common.mod.ModLoader

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

        elif func_name == "loadComplete":

            def run():
                runtime = Runtime()
                try:
                    runtime.run_method(function, None)
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        e.format_exception()
                    )
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

                        import mcpython.client.state.StateLoadingException
                        import mcpython.common.mod.ModLoader

                        mcpython.client.state.StateLoadingException.error_occur(
                            traceback.format_exc()
                        )
                        raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

            shared.mod_loader("minecraft", "stage:post")(run)

        else:
            print("missing BRIDGE binding for", function)

    @native(
        "addListener",
        "(Lnet/minecraftforge/eventbus/api/EventPriority;Ljava/util/function/Consumer;)V",
    )
    def addListener2(self, instance, priority, consumer):
        self.addListener(priority, consumer)

    @native("register", "(Ljava/lang/Object;)V")
    def register(self, instance, obj):
        pass

    @native("addGenericListener", "(Ljava/lang/Class;Ljava/util/function/Consumer;)V")
    def addGenericListener(self, instance, cls, consumer):
        return
        # todo: implement
        current_mod = shared.CURRENT_EVENT_SUB
        if cls.name == "net/minecraft/block/Block":

            @shared.mod_loader("minecraft", "stage:block:factory_usage")
            def load():
                shared.CURRENT_EVENT_SUB = current_mod

                runtime = Runtime()

                try:
                    runtime.run_method(
                        consumer, shared.registry.get_by_name("minecraft:block")
                    )
                except StackCollectingException as e:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        e.format_exception()
                    )
                    logger.write_into_container(e.format_exception())
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None
                except:
                    import mcpython.client.state.StateLoadingException

                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
                    traceback.print_exc()
                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

    @native(
        "addGenericListener",
        "(Ljava/lang/Class;Lnet/minecraftforge/eventbus/api/EventPriority;ZLjava/lang/Class;Ljava/util/function/Consumer;)V",
    )
    def addGenericListener2(self, instance, cls, priority, b, cls2, consumer):
        pass

    @native("post", "(Lnet/minecraftforge/eventbus/api/Event;)Z")
    def post(self, instance, event):
        pass


class DistMarker(NativeClass):
    NAME = "net/minecraftforge/api/distmarker/Dist"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "CLIENT": "client",
                "SERVER": "server",
                "DEDICATED_SERVER": "dedicated_server",
            }
        )

    @native("isClient", "()Z")
    def isClient(self, instance):
        return int(instance == "client")


class FMLEnvironment(NativeClass):
    NAME = "net/minecraftforge/fml/loading/FMLEnvironment"

    def __init__(self):
        super().__init__()
        self.exposed_attributes["dist"] = "client" if shared.IS_CLIENT else "server"
        self.exposed_attributes["production"] = 1


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

    @native(
        "unsafeCallWhenOn",
        "(Lnet/minecraftforge/api/distmarker/Dist;Ljava/util/function/Supplier;)Ljava/lang/Object;",
    )
    def unsafeCallWhenOn(self, dist, supplier):
        pass

    @native(
        "runWhenOn",
        "(Lnet/minecraftforge/api/distmarker/Dist;Ljava/util/function/Supplier;)V",
    )
    def runWhenOn(self, *_):
        pass

    @native(
        "unsafeRunWhenOn",
        "(Lnet/minecraftforge/api/distmarker/Dist;Ljava/util/function/Supplier;)V",
    )
    def unsafeRunWhenOn(self, *_):
        pass

    @native(
        "callWhenOn",
        "(Lnet/minecraftforge/api/distmarker/Dist;Ljava/util/function/Supplier;)Ljava/lang/Object;",
    )
    def callWhenOn(self, *_):
        pass

    @native(
        "safeRunWhenOn",
        "(Lnet/minecraftforge/api/distmarker/Dist;Ljava/util/function/Supplier;)V",
    )
    def safeRunWhenOn(self, *_):
        pass

    @native(
        "safeRunForDist",
        "(Ljava/util/function/Supplier;Ljava/util/function/Supplier;)Ljava/lang/Object;",
    )
    def safeRunForDist(self, *_):
        pass


class FMLPaths(NativeClass):
    NAME = "net/minecraftforge/fml/loading/FMLPaths"

    def __init__(self):
        super().__init__()
        config_dir = self.create_instance()
        config_dir.dir = shared.home + "/fml_configs"

        game_dir = self.create_instance()
        game_dir.dir = shared.home

        self.exposed_attributes = {"CONFIGDIR": config_dir, "GAMEDIR": game_dir}

    @native("get", "()Ljava/nio/file/Path;")
    def get(self, instance):
        obj = self.vm.get_class("java/io/Path", version=self.internal_version)
        obj.path = instance.dir
        return obj

    @native("getOrCreateGameRelativePath", "(Ljava/nio/file/Path;Ljava/lang/String;)Ljava/nio/file/Path;")
    def getOrCreateGameRelativePath(self, path, sub):
        return path  # todo: implement


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
        "defineInRange",
        "(Ljava/lang/String;DDD)Lnet/minecraftforge/common/ForgeConfigSpec$DoubleValue;",
    )
    def defineInRange2(self, instance, name: str, a, b, c):
        pass

    @native(
        "defineList",
        "(Ljava/lang/String;Ljava/util/List;Ljava/util/function/Predicate;)Lnet/minecraftforge/common/ForgeConfigSpec$ConfigValue;",
    )
    def defineList(self, instance, name, a, b):
        return instance

    @native(
        "translation",
        "(Ljava/lang/String;)Lnet/minecraftforge/common/ForgeConfigSpec$Builder;",
    )
    def translation(self, instance, key: str):
        pass

    @native("worldRestart", "()Lnet/minecraftforge/common/ForgeConfigSpec$Builder;")
    def worldRestart(self, *_):
        pass

    @native("get", "()Ljava/lang/Object;")
    def get(self, instance):
        pass


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
        return
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


class ModList(NativeClass):
    NAME = "net/minecraftforge/fml/ModList"

    @native("get", "()Lnet/minecraftforge/fml/ModList;")
    def getModList(self):
        return self

    @native("isLoaded", "(Ljava/lang/String;)Z")
    def isLoaded(self, instance, name: str):
        return int(name in shared.mod_loader.mods)

    @native("getModFileById", "(Ljava/lang/String;)Lnet/minecraftforge/fml/loading/moddiscovery/ModFileInfo;")
    def getModFileById(self, instance, name: str):
        return shared.mod_loader.mods[name]


class ModFileInfo(NativeClass):
    NAME = "net/minecraftforge/fml/loading/moddiscovery/ModFileInfo"

    @native("getFile", "()Lnet/minecraftforge/fml/loading/moddiscovery/ModFile;")
    def getFile(self, instance):
        return instance.path


class ModFile(NativeClass):
    NAME = "net/minecraftforge/fml/loading/moddiscovery/ModFile"

    @native("getScanResult", "()Lnet/minecraftforge/forgespi/language/ModFileScanData;")
    def getScanResult(self, instance):
        pass


class ModFileScanData(NativeClass):
    NAME = "net/minecraftforge/forgespi/language/ModFileScanData"

    @native("getAnnotations", "()Ljava/util/Set;")
    def getAnnotations(self, instance):
        return set()


class Event(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/Event"

    @native("<init>", "()V")
    def init(self, instance):
        pass


class EventPriority(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/EventPriority"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update(
            {
                "HIGHEST": 0,
                "HIGH": 1,
                "NORMAL": 2,
                "LOW": 3,
                "LOWEST": 4,
            }
        )


class IEnvironment__Keys(NativeClass):
    NAME = "cpw/mods/modlauncher/api/IEnvironment$Keys"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"VERSION": 1})


class Launcher(NativeClass):
    NAME = "cpw/mods/modlauncher/Launcher"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"INSTANCE": self.create_instance()})

    @native("environment", "()Lcpw/mods/modlauncher/Environment;")
    def environment(self, *_):
        pass


class Cancelable(NativeClass):
    NAME = "net/minecraftforge/eventbus/api/Cancelable"

    def on_annotate(self, cls, args):
        pass


class ObfuscationReflectionHelper(NativeClass):
    NAME = "net/minecraftforge/fml/common/ObfuscationReflectionHelper"

    @native(
        "findField", "(Ljava/lang/Class;Ljava/lang/String;)Ljava/lang/reflect/Field;"
    )
    def findField(self, cls, name):
        return cls.fields[name] if hasattr(cls, name) else None


class DeferredWorkQueue(NativeClass):
    NAME = "net/minecraftforge/fml/DeferredWorkQueue"

    @native(
        "runLater", "(Ljava/lang/Runnable;)Ljava/util/concurrent/CompletableFuture;"
    )
    def runLater(self, *_):
        pass


class ExtensionPoint(NativeClass):
    NAME = "net/minecraftforge/fml/ExtensionPoint"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "DISPLAYTEST": 0,
        })


class EventNetworkChannel(NativeClass):
    NAME = "net/minecraftforge/fml/event/EventNetworkChannel"
