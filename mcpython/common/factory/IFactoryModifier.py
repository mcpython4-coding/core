import typing

import mcpython.common.event.Registry


class IFactory:
    pass


class IFactoryModifier:
    def __init__(self):
        self.subscriber = []

    def on_apply(self,
                 target: typing.Callable[
                     [IFactory, mcpython.common.event.Registry.IRegistryContent],
                     mcpython.common.event.Registry.IRegistryContent]
                 ):
        self.subscriber.append(target)

    def apply(self, factory: IFactory, instance: mcpython.common.event.Registry.IRegistryContent) -> mcpython.common.event.Registry.IRegistryContent:
        for target in self.subscriber:
            instance = target(factory, instance)
        return instance

