"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class RegistryInjectionHolder:
    def __init__(self, *args, **kwargs):
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
            for registry in self.registries:
                if registry.allow_argumented_injection and registry.is_valid(args[0].injectable):
                    registry.register(args[0])
                return args[0].injectable
        else:
            for registry in self.registries:
                if registry.is_valid(args[0]):
                    registry.register(args[0])
                    return args[0]

    def get_by_name(self, name: str):
        for registry in self.registries:
            if registry.name == name: return registry
        return None


G.registry = RegistryHandler()


class Registry:
    def __init__(self, name: str, inject_base_classes=[], check_function=None, injection_function=None,
                 allow_argumented_injection=False, classbased=True):
        self.name = name
        self.inject_base_classes = inject_base_classes
        self.check_function = check_function
        self.injection_function = injection_function
        self.allow_argumented_injection = allow_argumented_injection
        self.registered_objects = []
        G.eventhandler.add_event_name("registry:{}:on_object_register".format(name))
        self.locked = False
        self.classbased = classbased
        G.registry.registries.append(self)
        self.values = {}

    def is_valid(self, obj):
        if self.locked: return False
        if self.classbased:
            return (self.check_function and self.check_function(obj)) or any(
                [issubclass(obj, x) for x in self.inject_base_classes])
        else:
            t = type(obj)
            return (self.check_function and self.check_function(obj)) or any(
                [issubclass(t, x) for x in self.inject_base_classes])

    def register(self, obj):
        if self.locked: raise ValueError("can't register an object to an locked registry")
        self.registered_objects.append(obj)
        if self.injection_function: self.injection_function(self, obj)
        G.eventhandler.call("registry:{}:on_object_register".format(self.name))

    def lock(self): self.locked = True

    def unlock(self): self.locked = False

    def set_attribute(self, name: str, value):
        self.values[name] = value

    def get_attribute(self, name: str):
        return self.values[name]

