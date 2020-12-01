"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G, logger
import mcpython.logger
import mcpython.common.event.EventHandler


class IRegistryContent:
    NAME = "minecraft:unknown_registry_content"
    TYPE = "minecraft:unknown_registry_content_type"

    @classmethod
    def on_register(cls, registry): pass

    INFO = None   # can be used to display any special info in e.g. /registryinfo-command

    # returns some information about the class stored in registry. used in saves to determine if registry was changed,
    # so could also include an version. Must be pickle-able
    @classmethod
    def compressed_info(cls): return cls.NAME


class Registry:
    def __init__(self, name: str, registry_type_names: list, injection_function=None,
                 allow_argument_injection=False, class_based=True, dump_content_in_saves=True):
        self.name = name
        self.registry_type_names = registry_type_names
        self.injection_function = injection_function
        self.allow_argumented_injection = allow_argument_injection
        self.registered_object_map = {}
        self.locked = False
        self.class_based = class_based
        G.registry.registries.append(self)
        self.dump_content_in_saves = dump_content_in_saves

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("modloader:finished", self.lock)

    def is_valid(self, obj: IRegistryContent):
        return not self.locked and obj.TYPE in self.registry_type_names

    def register(self, obj: IRegistryContent, override_existing=True):
        if self.locked:
            logger.println("[WARN] can't register object '{}' to locked registry '{}'".format(obj, self.name))
            logger.println("[WARN] this feature of registering post-freeze WILL be removed in the future")
        if obj.NAME == "minecraft:unknown_registry_content":
            logger.println("can't register unnamed object '{}'".format(obj))
            logger.println("every registry object MUST have an unique name")
            return
        if not G.eventhandler.call_cancelable("registry:{}:register".format(self.name), self, obj, override_existing): return
        if obj.NAME in self.registered_object_map and override_existing: return
        self.registered_object_map[obj.NAME] = obj
        if self.injection_function: self.injection_function(self, obj)
        obj.on_register(self)

    def lock(self): self.locked = True

    def unlock(self): self.locked = False


class RegistryInjectionHolder:
    def __init__(self, *args, **kwargs):   # todo: do something with the args and kwargs!
        self.args = args
        self.kwargs = kwargs
        self.injectable = None

    def __call__(self, obj):
        self.injectable = obj
        G.registry(self)


class RegistryHandler:
    def __init__(self):
        self.registries = []

    def __call__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0: raise ValueError("can't register. no object provided")
        elif len(args) > 1 or len(kwargs) > 0:  # create an injectable object instance
            return RegistryInjectionHolder(*args, **kwargs)
        elif type(args[0]) == RegistryInjectionHolder:
            if not issubclass(args[0].inhectable, IRegistryContent):
                raise ValueError("can't register. Object {} is NO sub-class of IRegistryContent".format(
                    args[0].injectable))
            for registry in self.registries:
                if registry.allow_argumented_injection and registry.is_valid(args[0].injectable):
                    registry.register(args[0])
                return args[0].injectable
        else:
            if not issubclass(args[0], IRegistryContent):
                raise ValueError("can't register. Object {} is NO sub-class of IRegistryContent".format(args[0]))
            for registry in self.registries:
                if registry.is_valid(args[0]):
                    registry.register(args[0])
                    return args[0]

    def get_by_name(self, name: str) -> Registry:
        for registry in self.registries:
            if registry.name == name: return registry
        return None

    def register(self, *args, **kwargs):
        return self(*args, **kwargs)

    def async_register(self, mod: str, phase: str):
        return lambda obj: G.modloader(mod, phase)(lambda: self.register(obj))


G.registry = RegistryHandler()

