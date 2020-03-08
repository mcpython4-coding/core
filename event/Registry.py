"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import logger


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
                 allow_argument_injection=False, class_based=True):
        self.name = name
        self.registry_type_names = registry_type_names
        self.injection_function = injection_function
        self.allow_argumented_injection = allow_argument_injection
        self.registered_object_map = {}
        self.locked = False
        self.class_based = class_based
        G.registry.registries.append(self)
        self.CANCEL_REGISTRATION = False

    def is_valid(self, obj: IRegistryContent):
        return not self.locked and obj.TYPE in self.registry_type_names

    def register(self, obj: IRegistryContent, override_existing=True):
        if self.locked: raise ValueError("can't register an object to an locked registry")
        if obj.NAME == "minecraft:unknown_registry_content":
            raise ValueError("can't register unnamed object {}".format(obj))
        self.CANCEL_REGISTRATION = False
        G.eventhandler.call("registry:{}:on_object_register".format(self.name), self, obj)
        if self.CANCEL_REGISTRATION: return
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


G.registry = RegistryHandler()

